from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from typing import List, Optional
from datetime import datetime

from models.email import (
    Email, 
    EmailSendRequest, 
    EmailSendResponse,
    EmailFetchResponse,
    EmailUpdateRequest,
    EmailSearchRequest
)
from services.email_service import email_service
from services.user_service_client import user_service_client

router = APIRouter(prefix="/emails", tags=["emails"])

async def get_current_user(authorization: str = Header(None)):
    """Extract and verify user from Authorization header"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = authorization.split(" ")[1]
    user_data = await user_service_client.verify_token(token)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user_data

@router.post("/fetch", response_model=EmailFetchResponse)
async def fetch_user_emails(current_user = Depends(get_current_user)):
    """Fetch emails for current user from Gmail"""
    result = await email_service.fetch_emails(current_user["user_id"])
    return EmailFetchResponse(**result)

@router.get("/", response_model=List[Email])
async def get_emails(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    read: Optional[bool] = Query(None),
    sender: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    current_user = Depends(get_current_user)
):
    """Get emails for current user with filtering and pagination"""
    filters = {
        "read": read,
        "sender": sender,
        "subject": subject
    }
    
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}
    
    emails = email_service.search_emails(current_user["user_id"], filters)
    
    # Apply pagination
    paginated_emails = emails[skip:skip + limit]
    
    return [Email(**email) for email in paginated_emails]

@router.get("/{email_id}", response_model=Email)
async def get_single_email(
    email_id: str,
    current_user = Depends(get_current_user)
):
    """Get a single email by ID"""
    email = email_service.get_email(current_user["user_id"], email_id)
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    return Email(**email)

@router.put("/{email_id}/read")
async def mark_email_as_read(
    email_id: str,
    update: EmailUpdateRequest,
    current_user = Depends(get_current_user)
):
    """Mark email as read/unread"""
    updates = {}
    if update.read is not None:
        updates["read"] = update.read
    
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No updates provided"
        )
    
    success = email_service.update_email(
        current_user["user_id"], 
        email_id, 
        updates
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    return {"status": "success", "message": "Email updated successfully"}

@router.post("/send", response_model=EmailSendResponse)
async def send_user_email(
    request: EmailSendRequest,
    current_user = Depends(get_current_user)
):
    """Send an email from the user's Gmail account"""
    result = await email_service.send_email(
        user_id=current_user["user_id"],
        to=request.to,
        subject=request.subject,
        body=request.body,
        cc=request.cc,
        bcc=request.bcc
    )
    
    return EmailSendResponse(**result)

@router.delete("/{email_id}")
async def delete_single_email(
    email_id: str,
    current_user = Depends(get_current_user)
):
    """Delete an email"""
    success = email_service.delete_email(current_user["user_id"], email_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found or could not be deleted"
        )
    
    return {"status": "success", "message": "Email deleted successfully"}

@router.post("/search", response_model=List[Email])
async def search_emails(
    search_request: EmailSearchRequest,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user)
):
    """Advanced email search"""
    filters = search_request.dict(exclude_none=True)
    
    emails = email_service.search_emails(current_user["user_id"], filters)
    
    # Apply pagination
    paginated_emails = emails[skip:skip + limit]
    
    return [Email(**email) for email in paginated_emails]

@router.get("/stats/summary")
async def get_email_stats(current_user = Depends(get_current_user)):
    """Get email statistics for the user"""
    from db.mongodb import get_email_collection
    
    email_collection = get_email_collection()
    user_id = current_user["user_id"]
    
    try:
        # Get total count
        total = email_collection.count_documents({"user_id": user_id})
        
        # Get unread count
        unread = email_collection.count_documents({
            "user_id": user_id, 
            "read": False
        })
        
        # Get count by time periods
        from datetime import timedelta
        now = datetime.utcnow()
        today = email_collection.count_documents({
            "user_id": user_id,
            "timestamp": {"$gte": now.replace(hour=0, minute=0, second=0, microsecond=0)}
        })
        
        this_week = email_collection.count_documents({
            "user_id": user_id,
            "timestamp": {"$gte": now - timedelta(days=7)}
        })
        
        return {
            "total_emails": total,
            "unread_emails": unread,
            "read_emails": total - unread,
            "today": today,
            "this_week": this_week
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting email stats: {str(e)}"
        )
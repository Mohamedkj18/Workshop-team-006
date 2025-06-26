
from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from typing import List, Optional
from datetime import datetime

from models.email import (
    Email, 
    EmailSendRequest, 
    EmailSendResponse,
    EmailFetchResponse,
    EmailUpdateRequest,
    EmailSearchRequest,
    EmailReplyRequest
)
from services.email_service import email_service
from services.user_service_client import user_service_client
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException




router = APIRouter(prefix="/emails", tags=["emails"])
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_data = await user_service_client.verify_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user_data


@router.post("/fetch", response_model=EmailFetchResponse)
async def fetch_user_emails(current_user = Depends(get_current_user)):  # ASYNC - calls Gmail API
    """Fetch emails for current user from Gmail"""
    print(f"Starting fetch for user: {current_user['user_id']}")
    result = await email_service.fetch_emails(current_user["user_id"])  # Await needed
    print("Fetch result:", result)
    return EmailFetchResponse(**result)



@router.get("/", response_model=List[Email])
async def get_emails(  # NOT async - just database queries
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
    print("User ID:", current_user["user_id"])
    print("Filters:", filters)
    
    emails = await email_service.search_emails(current_user["user_id"], filters)  # Sync call
    print(f"Found {len(emails)} emails")
    
    # Apply pagination
    paginated_emails = emails[skip:skip + limit]
    
    return [Email(**email) for email in paginated_emails]

@router.put("/{email_id}/mark-read")
async def mark_email_as_read(
    email_id: str,
    current_user = Depends(get_current_user)
):
    """Mark email as read in both Gmail and database"""
    result = await email_service.mark_email_read(current_user["user_id"], email_id)
    
    if not result["success"]:
        # Determine appropriate status code based on error
        if "not found" in result["error"].lower():
            status_code = status.HTTP_404_NOT_FOUND
        elif "service not available" in result["error"].lower():
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        else:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
        raise HTTPException(
            status_code=status_code,
            detail=result["error"]
        )
    
    # Success response with detailed information
    response = {
        "status": "success",
        "message": result["message"]
    }
    
    # Add additional info if available
    if "gmail_updated" in result:
        response["gmail_synced"] = result["gmail_updated"]
    if "database_updated" in result:
        response["database_updated"] = result["database_updated"]
    
    return response



@router.put("/{email_id}/mark-unread")
async def mark_email_as_unread(
    email_id: str,
    current_user = Depends(get_current_user)
):
    """Mark email as unread in both Gmail and database"""
    success = await email_service.mark_email_unread(current_user["user_id"], email_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found or could not be marked as unread"
        )
    
    return {
        "status": "success", 
        "message": "Email marked as unread successfully"
    }


@router.post("/send", response_model=EmailSendResponse)
async def send_user_email(  # ASYNC - calls Gmail API
    request: EmailSendRequest,
    current_user = Depends(get_current_user)
):
    """Send an email from the user's Gmail account"""
    result = await email_service.send_email(  # Await needed
        user_id=current_user["user_id"],
        to=request.to,
        subject=request.subject,
        body=request.body,
        cc=request.cc,
        bcc=request.bcc
    )
    
    return EmailSendResponse(**result)



# Add a test endpoint for debugging
@router.get("/test-gmail-connection")
async def test_gmail_connection(current_user = Depends(get_current_user)):  # NOT async - just testing
    """Test Gmail API connection for debugging"""
    try:
        print(f"Testing Gmail connection for user: {current_user['user_id']}")
        
        # Test getting user profile from user service (sync)
        user_data = await user_service_client.get_user_profile(current_user["user_id"])
        print(f"User data from user service: {user_data is not None}")
        
        if not user_data:
            return {"error": "Cannot get user data from user service"}
        
        if not user_data.get("google_token"):
            return {"error": "No Google token found for user"}
        
        # Test Gmail service creation (sync)
        service = await email_service.get_gmail_service(current_user["user_id"])
        print(f"Gmail service created: {service is not None}")
        
        if not service:
            return {"error": "Cannot create Gmail service"}
        
        # Test basic Gmail API call
        try:
            profile = service.users().getProfile(userId='me').execute()
            return {
                "success": True,
                "email": profile.get('emailAddress'),
                "total_messages": profile.get('messagesTotal'),
                "total_threads": profile.get('threadsTotal'),
                "history_id": profile.get('historyId')
            }
        except Exception as e:
            return {"error": f"Gmail API call failed: {str(e)}"}
            
    except Exception as e:
        return {"error": f"Test failed: {str(e)}"}



@router.put("/{email_id}/update")
async def update_email(
    email_id: str,
    update: EmailUpdateRequest,
    current_user = Depends(get_current_user)
):
    """Update email properties in database (flexible updates)"""
    # Convert the request to a dict and remove None values
    updates = update.dict(exclude_none=True)
    
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No updates provided"
        )
    
    success = await email_service.update_email(
        current_user["user_id"], 
        email_id, 
        updates
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found or could not be updated"
        )
    
    return {
        "status": "success", 
        "message": "Email updated successfully",
        "updated_fields": list(updates.keys())
    }

@router.delete("/{email_id}")
async def delete_single_email(
    email_id: str,
    current_user=Depends(get_current_user)
):
    success = await email_service.delete_email(current_user["user_id"], email_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found or could not be deleted"
        )

    return {"status": "success", "message": "Email deleted successfully"}


# SHOULD TEST
@router.post("/search", response_model=List[Email])
async def search_emails(  
    search_request: EmailSearchRequest,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user)
):
    """Advanced email search with DB-side pagination"""
    filters = search_request.dict(exclude_none=True)
    
    # Now search_emails handles pagination async in the DB!
    emails = await email_service.search_emails(
        current_user["user_id"], filters, skip=skip, limit=limit
    )
    
    return [Email(**email) for email in emails]

@router.get("/stats/summary")
async def get_email_stats(current_user = Depends(get_current_user)):
    """Get email statistics for the user (async version)"""
    from db.mongodb import get_email_collection
    
    email_collection = get_email_collection()
    user_id = current_user["user_id"]
    
    try:
        now = datetime.utcnow()
        total = await email_collection.count_documents({"user_id": user_id})
        unread = await email_collection.count_documents({"user_id": user_id, "read": False})
        today = await email_collection.count_documents({
            "user_id": user_id,
            "timestamp": {"$gte": now.replace(hour=0, minute=0, second=0, microsecond=0)}
        })
        this_week = await email_collection.count_documents({
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




@router.get("/{email_id}", response_model=Email)
async def get_single_email(  # NOT async - just database query
    email_id: str,
    current_user = Depends(get_current_user)
):
    """Get a single email by ID"""
    email = await email_service.get_email(current_user["user_id"], email_id)  # Sync call
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    return Email(**email)



@router.put("/{email_id}/trash")
async def move_email_to_trash(
    email_id: str,
    current_user = Depends(get_current_user)
):
    """Move email to trash in Gmail and update database"""
    result = await email_service.move_to_trash(current_user["user_id"], email_id)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in result["error"].lower() 
            else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"]
        )
    
    return {
        "status": "success", 
        "message": result["message"]
    }




@router.post("/{email_id}/reply")
async def reply_to_email(
    email_id: str,
    reply_request: EmailReplyRequest,
    current_user = Depends(get_current_user)
):
    """Reply to an email"""
    result = await email_service.reply_to_email(
        user_id=current_user["user_id"],
        email_id=email_id,
        reply_body=reply_request.body,
        reply_to_all=reply_request.reply_all,
        additional_cc=reply_request.cc,
        additional_bcc=reply_request.bcc
    )
    
    if not result["success"]:
        # Determine appropriate status code based on error
        if "not found" in result["error"].lower():
            status_code = status.HTTP_404_NOT_FOUND
        elif "service not available" in result["error"].lower():
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        else:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
        raise HTTPException(
            status_code=status_code,
            detail=result["error"]
        )
    
    return {
        "status": "success",
        "message": result["message"],
        "message_id": result.get("message_id"),
        "thread_id": result.get("thread_id")
    }
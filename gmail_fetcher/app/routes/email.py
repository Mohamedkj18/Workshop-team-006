from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from bson.objectid import ObjectId
from datetime import datetime
from jose import JWTError, jwt

from app.config import settings
from app.models.email import Email
from app.services.email_service import fetch_emails
from app.db.mongodb import get_email_collection

router = APIRouter(prefix="/emails", tags=["emails"])

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        if email is None or user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    return {"email": email, "user_id": user_id}

@router.post("/fetch")
async def fetch_user_emails(current_user = Depends(get_current_user)):
    """Fetch emails for current user"""
    result = fetch_emails(current_user["user_id"])
    return result

@router.get("/", response_model=List[Email])
async def get_emails(
    skip: int = 0,
    limit: int = 20,
    read: Optional[bool] = None,
    current_user = Depends(get_current_user)
):
    """Get emails for current user"""
    email_collection = get_email_collection()
    
    # Build query
    query = {"user_id": current_user["user_id"]}
    if read is not None:
        query["read"] = read
    
    # Get emails with pagination and sorting
    cursor = email_collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)
    
    # Convert to list of Email models
    emails = []
    for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        emails.append(Email(**doc))
    
    return emails

@router.put("/{email_id}/read")
async def mark_email_as_read(
    email_id: str,
    read: bool = True,
    current_user = Depends(get_current_user)
):
    """Mark email as read/unread"""
    email_collection = get_email_collection()
    
    try:
        # Update email read status
        result = email_collection.update_one(
            {"_id": ObjectId(email_id), "user_id": current_user["user_id"]},
            {"$set": {"read": read}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not found"
            )
            
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
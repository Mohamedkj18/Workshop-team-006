# from fastapi import APIRouter, Depends, HTTPException, status, Header, Query, Request
# from typing import List, Optional
# from datetime import datetime, timedelta
# import json

# from models.email import (
#     Email, 
#     EmailSendRequest, 
#     EmailSendResponse,
#     EmailFetchResponse,
#     EmailUpdateRequest,
#     EmailSearchRequest,
#     EmailReplyRequest
# )
# from services.email_service import email_service
# from services.user_service_client import user_service_client

# router = APIRouter(prefix="/emails", tags=["emails"])

# async def get_user_from_token(authorization: str = Header(...)) -> dict:
#     """Extract and verify token, return user data"""
#     print("this is the authorization:\n", authorization)

#     if not authorization.startswith("Bearer "):
#         raise HTTPException(status_code=401, detail="Invalid authorization header")
    
#     token = authorization.replace("Bearer ", "")
#     print("this is token\n", token)
#     user_data = await user_service_client.verify_token(token)
    
#     if not user_data:
#         raise HTTPException(status_code=401, detail="Invalid or expired token")
    
#     print("\ni got here\n")
#     return user_data

# @router.post("/fetch", response_model=EmailFetchResponse)
# async def fetch_user_emails(authorization: str = Header(...)):
#     """Fetch emails for current user from Gmail"""
#     user_data = await get_user_from_token(authorization)
#     user_id = user_data.get("user_id") or user_data.get("id") or user_data.get("_id")
    
#     print(f"Starting fetch for user: {user_id}")
#     result = await email_service.fetch_emails(str(user_id))
#     print("Fetch result:", result)
#     return EmailFetchResponse(**result)

# @router.get("/", response_model=dict)
# async def get_emails(
#     skip: int = Query(0, ge=0),
#     limit: int = Query(20, ge=1, le=100),
#     read: Optional[bool] = Query(None),
#     sender: Optional[str] = Query(None),
#     subject: Optional[str] = Query(None),
#     query: Optional[str] = Query(None),
#     from_date: Optional[str] = Query(None),
#     to_date: Optional[str] = Query(None),
#     labels: Optional[str] = Query(None),
#     authorization: str = Header(...)
# ):
#     """Get emails for current user with filtering and pagination"""
#     user_data = await get_user_from_token(authorization)
#     user_id = user_data.get("user_id") or user_data.get("id") or user_data.get("_id")
    
#     # Build filters
#     filters = {}
#     if read is not None:
#         filters["read"] = read
#     if sender:
#         filters["sender"] = sender
#     if subject:
#         filters["subject"] = subject
#     if query:
#         filters["query"] = query
#     if from_date:
#         try:
#             filters["from_date"] = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
#         except ValueError:
#             raise HTTPException(status_code=400, detail="Invalid from_date format")
#     if to_date:
#         try:
#             filters["to_date"] = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
#         except ValueError:
#             raise HTTPException(status_code=400, detail="Invalid to_date format")
#     if labels:
#         filters["labels"] = labels.split(",")
    
#     print("User ID:", user_id)
#     print("Filters:", filters)
    
#     emails = await email_service.search_emails(str(user_id), filters)
#     print(f"Found {len(emails)} emails")
    
#     # Apply pagination
#     total = len(emails)
#     paginated_emails = emails[skip:skip + limit]
    
#     return {
#         "emails": paginated_emails,
#         "total": total,
#         "skip": skip,
#         "limit": limit,
#         "has_more": skip + limit < total
#     }

# @router.get("/{email_id}", response_model=Email)
# async def get_single_email(
#     email_id: str,
#     authorization: str = Header(...)
# ):
#     """Get a single email by ID"""
#     user_data = await get_user_from_token(authorization)
#     user_id = user_data.get("user_id") or user_data.get("id") or user_data.get("_id")
    
#     email = await email_service.get_email(str(user_id), email_id)
    
#     if not email:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Email not found"
#         )
    
#     return Email(**email)

# @router.post("/send", response_model=EmailSendResponse)
# async def send_user_email(
#     request: Request,
#     authorization: str = Header(...)
# ):
#     """Send an email from the user's Gmail account"""
#     user_data = await get_user_from_token(authorization)
#     user_id = user_data.get("user_id") or user_data.get("id") or user_data.get("_id")
    
#     try:
#         body = await request.json()
#     except json.JSONDecodeError:
#         raise HTTPException(status_code=400, detail="Invalid JSON in request body")
    
#     # Validate required fields
#     if not body.get("to"):
#         raise HTTPException(status_code=400, detail="Recipients (to) field is required")
#     if not body.get("subject"):
#         raise HTTPException(status_code=400, detail="Subject field is required")
#     if not body.get("body"):
#         raise HTTPException(status_code=400, detail="Body field is required")
    
#     result = await email_service.send_email(
#         user_id=str(user_id),
#         to=body["to"],
#         subject=body["subject"],
#         body=body["body"],
#         cc=body.get("cc"),
#         bcc=body.get("bcc")
#     )
    
#     return EmailSendResponse(**result)

# @router.post("/{email_id}/reply")
# async def reply_to_email(
#     email_id: str,
#     request: Request,
#     authorization: str = Header(...)
# ):
#     """Reply to an email"""
#     user_data = await get_user_from_token(authorization)
#     user_id = user_data.get("user_id") or user_data.get("id") or user_data.get("_id")
    
#     try:
#         body = await request.json()
#     except json.JSONDecodeError:
#         raise HTTPException(status_code=400, detail="Invalid JSON in request body")
    
#     if not body.get("reply_body"):
#         raise HTTPException(status_code=400, detail="reply_body field is required")
    
#     result = await email_service.reply_to_email(
#         user_id=str(user_id),
#         email_id=email_id,
#         reply_body=body["reply_body"],
#         reply_to_all=body.get("reply_to_all", False),
#         additional_cc=body.get("additional_cc"),
#         additional_bcc=body.get("additional_bcc")
#     )
    
#     if not result["success"]:
#         if "not found" in result["error"].lower():
#             status_code = status.HTTP_404_NOT_FOUND
#         elif "service not available" in result["error"].lower():
#             status_code = status.HTTP_503_SERVICE_UNAVAILABLE
#         else:
#             status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
#         raise HTTPException(status_code=status_code, detail=result["error"])
    
#     return {
#         "status": "success",
#         "message": result["message"],
#         "message_id": result.get("message_id"),
#         "thread_id": result.get("thread_id")
#     }

# @router.post("/{email_id}/forward")
# async def forward_email(
#     email_id: str,
#     request: Request,
#     authorization: str = Header(...)
# ):
#     """Forward an email to other recipients"""
#     user_data = await get_user_from_token(authorization)
#     user_id = user_data.get("user_id") or user_data.get("id") or user_data.get("_id")
    
#     try:
#         body = await request.json()
#     except json.JSONDecodeError:
#         raise HTTPException(status_code=400, detail="Invalid JSON in request body")
    
#     if not body.get("to"):
#         raise HTTPException(status_code=400, detail="Recipients (to) field is required")
    
#     result = await email_service.forward_email(
#         user_id=str(user_id),
#         email_id=email_id,
#         to=body["to"],
#         forward_message=body.get("forward_message", ""),
#         cc=body.get("cc"),
#         bcc=body.get("bcc")
#     )
    
#     if not result["success"]:
#         if "not found" in result["error"].lower():
#             status_code = status.HTTP_404_NOT_FOUND
#         elif "service not available" in result["error"].lower():
#             status_code = status.HTTP_503_SERVICE_UNAVAILABLE
#         else:
#             status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
#         raise HTTPException(status_code=status_code, detail=result["error"])
    
#     return {
#         "status": "success",
#         "message": result["message"],
#         "message_id": result.get("message_id"),
#         "thread_id": result.get("thread_id")
#     }

# @router.put("/{email_id}/mark-read")
# async def mark_email_as_read(
#     email_id: str,
#     authorization: str = Header(...)
# ):
#     """Mark email as read in both Gmail and database"""
#     user_data = await get_user_from_token(authorization)
#     user_id = user_data.get("user_id") or user_data.get("id") or user_data.get("_id")
    
#     result = await email_service.mark_email_read(str(user_id), email_id)
    
#     if not result["success"]:
#         if "not found" in result["error"].lower():
#             status_code = status.HTTP_404_NOT_FOUND
#         elif "service not available" in result["error"].lower():
#             status_code = status.HTTP_503_SERVICE_UNAVAILABLE
#         else:
#             status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
#         raise HTTPException(status_code=status_code, detail=result["error"])
    
#     response = {
#         "status": "success",
#         "message": result["message"]
#     }
    
#     if "gmail_updated" in result:
#         response["gmail_synced"] = result["gmail_updated"]
#     if "database_updated" in result:
#         response["database_updated"] = result["database_updated"]
    
#     return response

# @router.put("/{email_id}/mark-unread")
# async def mark_email_as_unread(
#     email_id: str,
#     authorization: str = Header(...)
# ):
#     """Mark email as unread in both Gmail and database"""
#     user_data = await get_user_from_token(authorization)
#     user_id = user_data.get("user_id") or user_data.get("id") or user_data.get("_id")
    
#     success = await email_service.mark_email_unread(str(user_id), email_id)
    
#     if not success:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Email not found or could not be marked as unread"
#         )
    
#     return {
#         "status": "success", 
#         "message": "Email marked as unread successfully"
#     }

# @router.put("/{email_id}/update")
# async def update_email(
#     email_id: str,
#     request: Request,
#     authorization: str = Header(...)
# ):
#     """Update email properties in database"""
#     user_data = await get_user_from_token(authorization)
#     user_id = user_data.get("user_id") or user_data.get("id") or user_data.get("_id")
    
#     try:
#         updates = await request.json()
#     except json.JSONDecodeError:
#         raise HTTPException(status_code=400, detail="Invalid JSON in request body")
    
#     # Remove any fields that shouldn't be updated
#     forbidden_fields = ["user_id", "message_id", "_id", "id"]
#     for field in forbidden_fields:
#         updates.pop(field, None)
    
#     if not updates:
#         raise HTTPException(status_code=400, detail="No valid fields to update")
    
#     success = await email_service.update_email(str(user_id), email_id, updates)
    
#     if not success:
#         raise HTTPException(status_code=400, detail="Failed to update email")
    
#     return {
#         "status": "success", 
#         "message": "Email updated successfully",
#         "updated_fields": list(updates.keys())
#     }

# @router.delete("/{email_id}")
# async def delete_single_email(
#     email_id: str,
#     authorization: str = Header(...)
# ):
#     """Delete an email by ID"""
#     user_data = await get_user_from_token(authorization)
#     user_id = user_data.get("user_id") or user_data.get("id") or user_data.get("_id")
    
#     success = await email_service.delete_email(str(user_id), email_id)

#     if not success:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Email not found or could not be deleted"
#         )

#     return {"status": "success", "message": "Email deleted successfully"}

# @router.put("/{email_id}/trash")
# async def move_email_to_trash(
#     email_id: str,
#     authorization: str = Header(...)
# ):
#     """Move email to trash in Gmail and update database"""
#     user_data = await get_user_from_token(authorization)
#     user_id = user_data.get("user_id") or user_data.get("id") or user_data.get("_id")
    
#     result = await email_service.move_to_trash(str(user_id), email_id)
    
#     if not result["success"]:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND if "not found" in result["error"].lower() 
#             else status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=result["error"]
#         )
    
#     return {
#         "status": "success", 
#         "message": result["message"]
#     }

# @router.post("/search")
# async def search_emails(
#     request: Request,
#     skip: int = Query(0, ge=0),
#     limit: int = Query(20, ge=1, le=100),
#     authorization: str = Header(...)
# ):
#     """Advanced email search with pagination"""
#     user_data = await get_user_from_token(authorization)
#     user_id = user_data.get("user_id") or user_data.get("id") or user_data.get("_id")
    
#     try:
#         filters = await request.json()
#     except json.JSONDecodeError:
#         raise HTTPException(status_code=400, detail="Invalid JSON in request body")
    
#     # Convert date strings to datetime objects if present
#     for date_field in ["from_date", "to_date"]:
#         if filters.get(date_field):
#             try:
#                 filters[date_field] = datetime.fromisoformat(filters[date_field].replace('Z', '+00:00'))
#             except ValueError:
#                 raise HTTPException(status_code=400, detail=f"Invalid {date_field} format")
    
#     emails = await email_service.search_emails(str(user_id), filters)
    
#     # Apply pagination
#     total = len(emails)
#     paginated_emails = emails[skip:skip + limit]
    
#     return {
#         "emails": paginated_emails,
#         "total": total,
#         "skip": skip,
#         "limit": limit,
#         "has_more": skip + limit < total
#     }

# @router.get("/stats/summary")
# async def get_email_stats(authorization: str = Header(...)):
#     """Get email statistics for the user"""
#     user_data = await get_user_from_token(authorization)
#     user_id = user_data.get("user_id") or user_data.get("id") or user_data.get("_id")
    
#     from db.mongodb import get_email_collection
    
#     email_collection = get_email_collection()
    
#     try:
#         now = datetime.utcnow()
#         total = await email_collection.count_documents({"user_id": str(user_id)})
#         unread = await email_collection.count_documents({"user_id": str(user_id), "read": False})
#         today = await email_collection.count_documents({
#             "user_id": str(user_id),
#             "timestamp": {"$gte": now.replace(hour=0, minute=0, second=0, microsecond=0)}
#         })
#         this_week = await email_collection.count_documents({
#             "user_id": str(user_id),
#             "timestamp": {"$gte": now - timedelta(days=7)}
#         })
        
#         return {
#             "total_emails": total,
#             "unread_emails": unread,
#             "read_emails": total - unread,
#             "today": today,
#             "this_week": this_week
#         }
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error getting email stats: {str(e)}"
#         )

# @router.get("/test-gmail-connection")
# async def test_gmail_connection(authorization: str = Header(...)):
#     """Test Gmail API connection for debugging"""
#     user_data = await get_user_from_token(authorization)
#     user_id = user_data.get("user_id") or user_data.get("id") or user_data.get("_id")
    
#     try:
#         print(f"Testing Gmail connection for user: {user_id}")
        
#         # Test getting user profile from user service
#         user_profile = await user_service_client.get_user_profile(str(user_id))
#         print(f"User data from user service: {user_profile is not None}")
        
#         if not user_profile:
#             return {"error": "Cannot get user data from user service"}
        
#         if not user_profile.get("google_token"):
#             return {"error": "No Google token found for user"}
        
#         # Test Gmail service creation
#         service = await email_service.get_gmail_service(str(user_id))
#         print(f"Gmail service created: {service is not None}")
        
#         if not service:
#             return {"error": "Cannot create Gmail service"}
        
#         # Test basic Gmail API call
#         try:
#             import asyncio
#             loop = asyncio.get_running_loop()
#             profile = await loop.run_in_executor(
#                 None,
#                 lambda: service.users().getProfile(userId='me').execute()
#             )
#             return {
#                 "success": True,
#                 "email": profile.get('emailAddress'),
#                 "total_messages": profile.get('messagesTotal'),
#                 "total_threads": profile.get('threadsTotal'),
#                 "history_id": profile.get('historyId')
#             }
#         except Exception as e:
#             return {"error": f"Gmail API call failed: {str(e)}"}
            
#     except Exception as e:
#         return {"error": f"Test failed: {str(e)}"}

# @router.get("/health")
# async def health_check():
#     """Health check endpoint"""
#     return {"status": "healthy", "service": "email-service"}



from fastapi import APIRouter, Depends, HTTPException, status, Header, Query, Request
from typing import List, Optional
from datetime import datetime, timedelta
import json

from models.email import (
    Email, 
    EmailSendRequest, 
    EmailSendResponse,
    EmailFetchResponse,
    EmailUpdateRequest,
    EmailSearchRequest,
    EmailReplyRequest,
    EmailForwardRequest  # ✅ Added missing import
)
from services.email_service import email_service
from services.user_service_client import user_service_client

router = APIRouter(prefix="/emails", tags=["emails"])

async def get_user_from_token(authorization: str = Header(...)) -> dict:
    """Extract and verify token, return user data"""
    print("this is the authorization:\n", authorization)

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    print("this is token\n", token)
    user_data = await user_service_client.verify_token(token)
    
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    print("\ni got here\n")
    return user_data

@router.post("/fetch", response_model=EmailFetchResponse)
async def fetch_user_emails(authorization: str = Header(...)):
    """Fetch emails for current user from Gmail"""
    user_data = await get_user_from_token(authorization)
    user_id = user_data.get("user_id") or user_data.get("id") or user_data.get("_id")
    
    print(f"Starting fetch for user: {user_id}")
    result = await email_service.fetch_emails(str(user_id))
    print("Fetch result:", result)
    return EmailFetchResponse(**result)

@router.get("/", response_model=dict)
async def get_emails(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    read: Optional[bool] = Query(None),
    sender: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    query: Optional[str] = Query(None),
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    labels: Optional[str] = Query(None),
    authorization: str = Header(...)
):
    """Get emails for current user with filtering and pagination"""
    user_data = await get_user_from_token(authorization)
    user_id = user_data.get("user_id") or user_data.get("id") or user_data.get("_id")
    
    # Build filters
    filters = {}
    if read is not None:
        filters["read"] = read
    if sender:
        filters["sender"] = sender
    if subject:
        filters["subject"] = subject
    if query:
        filters["query"] = query
    if from_date:
        try:
            filters["from_date"] = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid from_date format")
    if to_date:
        try:
            filters["to_date"] = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid to_date format")
    if labels:
        filters["labels"] = labels.split(",")
    
    print("User ID:", user_id)
    print("Filters:", filters)
    
    emails = await email_service.search_emails(str(user_id), filters)
    print(f"Found {len(emails)} emails")
    
    # Apply pagination
    total = len(emails)
    paginated_emails = emails[skip:skip + limit]
    
    return {
        "emails": paginated_emails,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": skip + limit < total
    }

@router.get("/{email_id}", response_model=Email)
async def get_single_email(
    email_id: str,
    authorization: str = Header(...)
):
    """Get a single email by ID"""
    user_data = await get_user_from_token(authorization)
    user_id = user_data.get("user_id") or user_data.get("id") or user_data.get("_id")
    
    email = await email_service.get_email(str(user_id), email_id)
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    return Email(**email)

# ✅ FIXED - Now uses Pydantic model instead of Request
@router.post("/send", response_model=EmailSendResponse)
async def send_user_email(
    email_request: EmailSendRequest,  # ✅ Changed from Request to Pydantic model
    authorization: str = Header(...)
):
    """Send an email from the user's Gmail account"""
    user_data = await get_user_from_token(authorization)
    user_id = user_data.get("user_id") or user_data.get("id") or user_data.get("_id")
    
    print(f"[DEBUG] Send email request: {email_request.dict()}")
    
    result = await email_service.send_email(
        user_id=str(user_id),
        to=email_request.to,
        subject=email_request.subject,
        body=email_request.body,
        cc=email_request.cc,
        bcc=email_request.bcc
    )
    
    return EmailSendResponse(**result)

# ✅ FIXED - Now uses Pydantic model instead of Request
@router.post("/{email_id}/reply")
async def reply_to_email(
    email_id: str,
    reply_request: EmailReplyRequest,  # ✅ Changed from Request to Pydantic model
    authorization: str = Header(...)
):
    """Reply to an email"""
    user_data = await get_user_from_token(authorization)
    user_id = user_data.get("user_id") or user_data.get("id") or user_data.get("_id")
    
    print(f"[DEBUG] Reply request: {reply_request.dict()}")
    
    result = await email_service.reply_to_email(
        user_id=str(user_id),
        email_id=email_id,
        reply_body=reply_request.reply_body,
        reply_to_all=reply_request.reply_to_all,
        additional_cc=reply_request.additional_cc,
        additional_bcc=reply_request.additional_bcc
    )
    
    if not result["success"]:
        if "not found" in result["error"].lower():
            status_code = status.HTTP_404_NOT_FOUND
        elif "service not available" in result["error"].lower():
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        else:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
        raise HTTPException(status_code=status_code, detail=result["error"])
    
    return {
        "status": "success",
        "message": result["message"],
        "message_id": result.get("message_id"),
        "thread_id": result.get("thread_id")
    }

# ✅ FIXED - Now uses Pydantic model instead of Request
@router.post("/{email_id}/forward")
async def forward_email(
    email_id: str,
    forward_request: EmailForwardRequest,  # ✅ Changed from Request to Pydantic model
    authorization: str = Header(...)
):
    """Forward an email to other recipients"""
    user_data = await get_user_from_token(authorization)
    user_id = user_data.get("user_id") or user_data.get("id") or user_data.get("_id")
    
    print(f"[DEBUG] Forward request: {forward_request.dict()}")
    
    result = await email_service.forward_email(
        user_id=str(user_id),
        email_id=email_id,
        to=forward_request.to,
        forward_message=forward_request.forward_message,
        cc=forward_request.cc,
        bcc=forward_request.bcc
    )
    
    if not result["success"]:
        if "not found" in result["error"].lower():
            status_code = status.HTTP_404_NOT_FOUND
        elif "service not available" in result["error"].lower():
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        else:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
        raise HTTPException(status_code=status_code, detail=result["error"])
    
    return {
        "status": "success",
        "message": result["message"],
        "message_id": result.get("message_id"),
        "thread_id": result.get("thread_id")
    }

@router.put("/{email_id}/mark-read")
async def mark_email_as_read(
    email_id: str,
    authorization: str = Header(...)
):
    """Mark email as read in both Gmail and database"""
    user_data = await get_user_from_token(authorization)
    user_id = user_data.get("user_id") or user_data.get("id") or user_data.get("_id")
    
    result = await email_service.mark_email_read(str(user_id), email_id)
    
    if not result["success"]:
        if "not found" in result["error"].lower():
            status_code = status.HTTP_404_NOT_FOUND
        elif "service not available" in result["error"].lower():
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        else:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
        raise HTTPException(status_code=status_code, detail=result["error"])
    
    response = {
        "status": "success",
        "message": result["message"]
    }
    
    if "gmail_updated" in result:
        response["gmail_synced"] = result["gmail_updated"]
    if "database_updated" in result:
        response["database_updated"] = result["database_updated"]
    
    return response

@router.put("/{email_id}/mark-unread")
async def mark_email_as_unread(
    email_id: str,
    authorization: str = Header(...)
):
    """Mark email as unread in both Gmail and database"""
    user_data = await get_user_from_token(authorization)
    user_id = user_data.get("user_id") or user_data.get("id") or user_data.get("_id")
    
    success = await email_service.mark_email_unread(str(user_id), email_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found or could not be marked as unread"
        )
    
    return {
        "status": "success", 
        "message": "Email marked as unread successfully"
    }

# ✅ FIXED - Now uses Pydantic model instead of Request
@router.put("/{email_id}/update")
async def update_email(
    email_id: str,
    update_request: EmailUpdateRequest,  # ✅ Changed from Request to Pydantic model
    authorization: str = Header(...)
):
    """Update email properties in database"""
    user_data = await get_user_from_token(authorization)
    user_id = user_data.get("user_id") or user_data.get("id") or user_data.get("_id")
    
    # Convert Pydantic model to dict and exclude unset fields
    updates = update_request.dict(exclude_unset=True)
    print(f"[DEBUG] Update request: {updates}")
    
    # Remove any fields that shouldn't be updated
    forbidden_fields = ["user_id", "message_id", "_id", "id"]
    for field in forbidden_fields:
        updates.pop(field, None)
    
    if not updates:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    
    success = await email_service.update_email(str(user_id), email_id, updates)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update email")
    
    return {
        "status": "success", 
        "message": "Email updated successfully",
        "updated_fields": list(updates.keys())
    }

@router.delete("/{email_id}")
async def delete_single_email(
    email_id: str,
    authorization: str = Header(...)
):
    """Delete an email by ID"""
    user_data = await get_user_from_token(authorization)
    user_id = user_data.get("user_id") or user_data.get("id") or user_data.get("_id")
    
    success = await email_service.delete_email(str(user_id), email_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found or could not be deleted"
        )

    return {"status": "success", "message": "Email deleted successfully"}

@router.put("/{email_id}/trash")
async def move_email_to_trash(
    email_id: str,
    authorization: str = Header(...)
):
    """Move email to trash in Gmail and update database"""
    user_data = await get_user_from_token(authorization)
    user_id = user_data.get("user_id") or user_data.get("id") or user_data.get("_id")
    
    result = await email_service.move_to_trash(str(user_id), email_id)
    
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

# ✅ FIXED - Now uses Pydantic model instead of Request
@router.post("/search")
async def search_emails(
    search_request: EmailSearchRequest,  # ✅ Changed from Request to Pydantic model
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    authorization: str = Header(...)
):
    """Advanced email search with pagination"""
    user_data = await get_user_from_token(authorization)
    user_id = user_data.get("user_id") or user_data.get("id") or user_data.get("_id")
    
    # Convert Pydantic model to dict and handle date conversion
    filters = search_request.dict(exclude_unset=True)
    print(f"[DEBUG] Search request: {filters}")
    
    # Convert date strings to datetime objects if present
    for date_field in ["from_date", "to_date"]:
        if filters.get(date_field):
            try:
                filters[date_field] = datetime.fromisoformat(filters[date_field].replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid {date_field} format")
    
    emails = await email_service.search_emails(str(user_id), filters)
    
    # Apply pagination
    total = len(emails)
    paginated_emails = emails[skip:skip + limit]
    
    return {
        "emails": paginated_emails,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": skip + limit < total
    }

@router.get("/stats/summary")
async def get_email_stats(authorization: str = Header(...)):
    """Get email statistics for the user"""
    user_data = await get_user_from_token(authorization)
    user_id = user_data.get("user_id") or user_data.get("id") or user_data.get("_id")
    
    from db.mongodb import get_email_collection
    
    email_collection = get_email_collection()
    
    try:
        now = datetime.utcnow()
        total = await email_collection.count_documents({"user_id": str(user_id)})
        unread = await email_collection.count_documents({"user_id": str(user_id), "read": False})
        today = await email_collection.count_documents({
            "user_id": str(user_id),
            "timestamp": {"$gte": now.replace(hour=0, minute=0, second=0, microsecond=0)}
        })
        this_week = await email_collection.count_documents({
            "user_id": str(user_id),
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

@router.get("/test-gmail-connection")
async def test_gmail_connection(authorization: str = Header(...)):
    """Test Gmail API connection for debugging"""
    user_data = await get_user_from_token(authorization)
    user_id = user_data.get("user_id") or user_data.get("id") or user_data.get("_id")
    
    try:
        print(f"Testing Gmail connection for user: {user_id}")
        
        # Test getting user profile from user service
        user_profile = await user_service_client.get_user_profile(str(user_id))
        print(f"User data from user service: {user_profile is not None}")
        
        if not user_profile:
            return {"error": "Cannot get user data from user service"}
        
        if not user_profile.get("google_token"):
            return {"error": "No Google token found for user"}
        
        # Test Gmail service creation
        service = await email_service.get_gmail_service(str(user_id))
        print(f"Gmail service created: {service is not None}")
        
        if not service:
            return {"error": "Cannot create Gmail service"}
        
        # Test basic Gmail API call
        try:
            import asyncio
            loop = asyncio.get_running_loop()
            profile = await loop.run_in_executor(
                None,
                lambda: service.users().getProfile(userId='me').execute()
            )
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

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "email-service"}

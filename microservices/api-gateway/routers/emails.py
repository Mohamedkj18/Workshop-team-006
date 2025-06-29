from fastapi import APIRouter, Request, HTTPException, Query, Header
from typing import List, Optional
import httpx
import os
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
from models.emails import (
    EmailReplyRequest,
    EmailForwardRequest,
    EmailSendRequest,
    EmailUpdateRequest,
    EmailSearchRequest
    )



router = APIRouter(prefix="/emails", tags=["emails"])
security = HTTPBearer()

# Get service URLs from environment
EMAIL_SERVICE_URL = os.getenv("EMAIL_SERVICE_URL", "http://email-service:8000")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8000")

# Authentication dependency for gateway
async def verify_token_with_user_service(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify token with user service and return user data"""
    token = credentials.credentials
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{USER_SERVICE_URL}/auth/verify",
                json={"token": token}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("valid"):
                    return result.get("user"), token  # Return both user data and token
            
            raise HTTPException(status_code=401, detail="Invalid or expired token")
            
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="User service unavailable")

# Helper function to create headers with token
async def get_forwarded_headers(token: str) -> dict:
    """Create headers to forward to email service"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

# 1. FETCH EMAILS
@router.post("/fetch")
async def fetch_user_emails(auth_data = Depends(verify_token_with_user_service)):
    """Proxy: Fetch emails for current user from Gmail"""
    user_data, token = auth_data
    print("[DEBUG] this is auth_data\n\n", auth_data)
    try:
        headers = await get_forwarded_headers(token)
        print("[DEBUG] Fetching emails for user:", user_data.get("id"))
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{EMAIL_SERVICE_URL}/emails/fetch",
                headers=headers
            )
            response.raise_for_status()
            print("[DEBUG] Emails fetched successfully")
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Email service unavailable: {str(exc)}")

# # 2. GET EMAILS (List with filters and pagination)
# @router.get("/")
# async def get_emails(
#     skip: int = Query(0, ge=0),
#     limit: int = Query(20, ge=1, le=100),
#     read: Optional[bool] = Query(None),
#     sender: Optional[str] = Query(None),
#     subject: Optional[str] = Query(None),
#     auth_data = Depends(verify_token_with_user_service)
# ):
#     """Proxy: Get emails for current user with filtering and pagination"""
#     user_data, token = auth_data
    
#     try:
#         headers = await get_forwarded_headers(token)
#         params = {
#             "skip": skip,
#             "limit": limit
#         }
#         if read is not None:
#             params["read"] = read
#         if sender:
#             params["sender"] = sender
#         if subject:
#             params["subject"] = subject
            
#         async with httpx.AsyncClient() as client:
#             response = await client.get(
#                 f"{EMAIL_SERVICE_URL}/emails/",
#                 headers=headers,
#                 params=params
#             )
#             response.raise_for_status()
#             return response.json()
#     except httpx.HTTPStatusError as exc:
#         raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
#     except httpx.RequestError as exc:
#         raise HTTPException(status_code=503, detail=f"Email service unavailable: {str(exc)}")

# # 3. GET SINGLE EMAIL
# @router.get("/{email_id}")
# async def get_single_email(email_id: str, auth_data = Depends(verify_token_with_user_service)):
#     """Proxy: Get a specific email by ID"""
#     user_data, token = auth_data
    
#     try:
#         headers = await get_forwarded_headers(token)
#         async with httpx.AsyncClient() as client:
#             response = await client.get(
#                 f"{EMAIL_SERVICE_URL}/emails/{email_id}",
#                 headers=headers
#             )
#             response.raise_for_status()
#             return response.json()
#     except httpx.HTTPStatusError as exc:
#         raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
#     except httpx.RequestError as exc:
#         raise HTTPException(status_code=503, detail=f"Email service unavailable: {str(exc)}")

# # 4. SEND EMAIL
# @router.post("/send")
# async def send_email(request: Request, auth_data = Depends(verify_token_with_user_service)):
#     """Proxy: Send an email via the email service"""
#     user_data, token = auth_data
    
#     try:
#         body = await request.json()
#         headers = await get_forwarded_headers(token)
#         async with httpx.AsyncClient() as client:
#             response = await client.post(
#                 f"{EMAIL_SERVICE_URL}/emails/send",
#                 headers=headers,
#                 json=body
#             )
#             response.raise_for_status()
#             return response.json()
#     except httpx.HTTPStatusError as exc:
#         raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
#     except httpx.RequestError as exc:
#         raise HTTPException(status_code=503, detail=f"Email service unavailable: {str(exc)}")

# # 5. REPLY TO EMAIL
# @router.post("/{email_id}/reply")
# async def reply_to_email(email_id: str, request: Request, auth_data = Depends(verify_token_with_user_service)):
#     """Proxy: Reply to an email"""
#     user_data, token = auth_data
    
#     try:
#         body = await request.json()
#         headers = await get_forwarded_headers(token)
#         async with httpx.AsyncClient() as client:
#             response = await client.post(
#                 f"{EMAIL_SERVICE_URL}/emails/{email_id}/reply",
#                 headers=headers,
#                 json=body
#             )
#             response.raise_for_status()
#             return response.json()
#     except httpx.HTTPStatusError as exc:
#         raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
#     except httpx.RequestError as exc:
#         raise HTTPException(status_code=503, detail=f"Email service unavailable: {str(exc)}")

# # 6. FORWARD EMAIL
# @router.post("/{email_id}/forward")
# async def forward_email(email_id: str, request: Request, auth_data = Depends(verify_token_with_user_service)):
#     """Proxy: Forward an email"""
#     user_data, token = auth_data
    
#     try:
#         body = await request.json()
#         headers = await get_forwarded_headers(token)
#         async with httpx.AsyncClient() as client:
#             response = await client.post(
#                 f"{EMAIL_SERVICE_URL}/emails/{email_id}/forward",
#                 headers=headers,
#                 json=body
#             )
#             response.raise_for_status()
#             return response.json()
#     except httpx.HTTPStatusError as exc:
#         raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
#     except httpx.RequestError as exc:
#         raise HTTPException(status_code=503, detail=f"Email service unavailable: {str(exc)}")

# # 7. MARK EMAIL AS READ
# @router.put("/{email_id}/mark-read")
# async def mark_email_as_read(email_id: str, auth_data = Depends(verify_token_with_user_service)):
#     """Proxy: Mark email as read in both Gmail and database"""
#     user_data, token = auth_data
    
#     try:
#         headers = await get_forwarded_headers(token)
#         async with httpx.AsyncClient() as client:
#             response = await client.put(
#                 f"{EMAIL_SERVICE_URL}/emails/{email_id}/mark-read",
#                 headers=headers
#             )
#             response.raise_for_status()
#             return response.json()
#     except httpx.HTTPStatusError as exc:
#         raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
#     except httpx.RequestError as exc:
#         raise HTTPException(status_code=503, detail=f"Email service unavailable: {str(exc)}")

# # 8. MARK EMAIL AS UNREAD
# @router.put("/{email_id}/mark-unread")
# async def mark_email_as_unread(email_id: str, auth_data = Depends(verify_token_with_user_service)):
#     """Proxy: Mark email as unread in both Gmail and database"""
#     user_data, token = auth_data
    
#     try:
#         headers = await get_forwarded_headers(token)
#         async with httpx.AsyncClient() as client:
#             response = await client.put(
#                 f"{EMAIL_SERVICE_URL}/emails/{email_id}/mark-unread",
#                 headers=headers
#             )
#             response.raise_for_status()
#             return response.json()
#     except httpx.HTTPStatusError as exc:
#         raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
#     except httpx.RequestError as exc:
#         raise HTTPException(status_code=503, detail=f"Email service unavailable: {str(exc)}")

# # 9. UPDATE EMAIL
# @router.put("/{email_id}/update")
# async def update_email(email_id: str, request: Request, auth_data = Depends(verify_token_with_user_service)):
#     """Proxy: Update email properties in database"""
#     user_data, token = auth_data
    
#     try:
#         body = await request.json()
#         headers = await get_forwarded_headers(token)
#         async with httpx.AsyncClient() as client:
#             response = await client.put(
#                 f"{EMAIL_SERVICE_URL}/emails/{email_id}/update",
#                 headers=headers,
#                 json=body
#             )
#             response.raise_for_status()
#             return response.json()
#     except httpx.HTTPStatusError as exc:
#         raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
#     except httpx.RequestError as exc:
#         raise HTTPException(status_code=503, detail=f"Email service unavailable: {str(exc)}")

# # 10. DELETE EMAIL
# @router.delete("/{email_id}")
# async def delete_email(email_id: str, auth_data = Depends(verify_token_with_user_service)):
#     """Proxy: Delete an email by ID"""
#     user_data, token = auth_data
    
#     try:
#         headers = await get_forwarded_headers(token)
#         async with httpx.AsyncClient() as client:
#             response = await client.delete(
#                 f"{EMAIL_SERVICE_URL}/emails/{email_id}",
#                 headers=headers
#             )
#             response.raise_for_status()
#             return response.json()
#     except httpx.HTTPStatusError as exc:
#         raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
#     except httpx.RequestError as exc:
#         raise HTTPException(status_code=503, detail=f"Email service unavailable: {str(exc)}")

# # 11. MOVE TO TRASH
# @router.put("/{email_id}/trash")
# async def move_email_to_trash(email_id: str, auth_data = Depends(verify_token_with_user_service)):
#     """Proxy: Move email to trash in Gmail and update database"""
#     user_data, token = auth_data
    
#     try:
#         headers = await get_forwarded_headers(token)
#         async with httpx.AsyncClient() as client:
#             response = await client.put(
#                 f"{EMAIL_SERVICE_URL}/emails/{email_id}/trash",
#                 headers=headers
#             )
#             response.raise_for_status()
#             return response.json()
#     except httpx.HTTPStatusError as exc:
#         raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
#     except httpx.RequestError as exc:
#         raise HTTPException(status_code=503, detail=f"Email service unavailable: {str(exc)}")

# # 12. SEARCH EMAILS
# @router.post("/search")
# async def search_emails(
#     request: Request,
#     skip: int = Query(0, ge=0),
#     limit: int = Query(20, ge=1, le=100),
#     auth_data = Depends(verify_token_with_user_service)
# ):
#     """Proxy: Advanced email search with pagination"""
#     user_data, token = auth_data
    
#     try:
#         body = await request.json()
#         headers = await get_forwarded_headers(token)
#         params = {
#             "skip": skip,
#             "limit": limit
#         }
#         async with httpx.AsyncClient() as client:
#             response = await client.post(
#                 f"{EMAIL_SERVICE_URL}/emails/search",
#                 headers=headers,
#                 json=body,
#                 params=params
#             )
#             response.raise_for_status()
#             return response.json()
#     except httpx.HTTPStatusError as exc:
#         raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
#     except httpx.RequestError as exc:
#         raise HTTPException(status_code=503, detail=f"Email service unavailable: {str(exc)}")

# # 13. EMAIL STATISTICS
# @router.get("/stats/summary")
# async def get_email_stats(auth_data = Depends(verify_token_with_user_service)):
#     """Proxy: Get email statistics for the user"""
#     user_data, token = auth_data
    
#     try:
#         headers = await get_forwarded_headers(token)
#         async with httpx.AsyncClient() as client:
#             response = await client.get(
#                 f"{EMAIL_SERVICE_URL}/emails/stats/summary",
#                 headers=headers
#             )
#             response.raise_for_status()
#             return response.json()
#     except httpx.HTTPStatusError as exc:
#         raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
#     except httpx.RequestError as exc:
#         raise HTTPException(status_code=503, detail=f"Email service unavailable: {str(exc)}")

# # 14. TEST GMAIL CONNECTION
# @router.get("/test-gmail-connection")
# async def test_gmail_connection(auth_data = Depends(verify_token_with_user_service)):
#     """Proxy: Test Gmail API connection for debugging"""
#     user_data, token = auth_data
    
#     try:
#         headers = await get_forwarded_headers(token)
#         async with httpx.AsyncClient() as client:
#             response = await client.get(
#                 f"{EMAIL_SERVICE_URL}/emails/test-gmail-connection",
#                 headers=headers
#             )
#             response.raise_for_status()
#             return response.json()
#     except httpx.HTTPStatusError as exc:
#         raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
#     except httpx.RequestError as exc:
#         raise HTTPException(status_code=503, detail=f"Email service unavailable: {str(exc)}")

# # HEALTH CHECK FOR EMAIL SERVICE (No auth needed)
# @router.get("/health")
# async def email_service_health():
#     """Check if email service is healthy"""
#     try:
#         async with httpx.AsyncClient(timeout=5.0) as client:
#             response = await client.get(f"{EMAIL_SERVICE_URL}/health")
#             return {
#                 "status": "healthy" if response.status_code == 200 else "unhealthy",
#                 "email_service_status": response.status_code,
#                 "service_url": EMAIL_SERVICE_URL
#             }
#     except httpx.RequestError:
#         return {
#             "status": "unhealthy",
#             "email_service_status": "unavailable",
#             "error": "Email service is not reachable",
#             "service_url": EMAIL_SERVICE_URL
#         }


# @router.post("/fetch")
# async def fetch_user_emails(auth_data = Depends(verify_token_with_user_service)):
#     """Proxy: Fetch emails for current user from Gmail"""
#     user_data, token = auth_data
#     print("[DEBUG] this is auth_data\n\n", auth_data)
    
#     try:
#         headers = await get_forwarded_headers(token)
#         print("[DEBUG] Fetching emails for user:", user_data.get("id"))
#         async with httpx.AsyncClient(timeout=30.0) as client:
#             response = await client.post(
#                 f"{EMAIL_SERVICE_URL}/emails/fetch",
#                 headers=headers
#             )
#             response.raise_for_status()
#             print("[DEBUG] Emails fetched successfully")
#             return response.json()
#     except httpx.HTTPStatusError as exc:
#         raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
#     except httpx.RequestError as exc:
#         raise HTTPException(status_code=503, detail=f"Email service unavailable: {str(exc)}")

# 2. GET EMAILS (List with filters and pagination)
@router.get("/")
async def get_emails(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    read: Optional[bool] = Query(None),
    sender: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    auth_data = Depends(verify_token_with_user_service)
):
    """Proxy: Get emails for current user with filtering and pagination"""
    user_data, token = auth_data
    
    try:
        headers = await get_forwarded_headers(token)
        params = {
            "skip": skip,
            "limit": limit
        }
        if read is not None:
            params["read"] = read
        if sender:
            params["sender"] = sender
        if subject:
            params["subject"] = subject
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{EMAIL_SERVICE_URL}/emails/",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Email service unavailable: {str(exc)}")

# 3. GET SINGLE EMAIL
@router.get("/{email_id}")
async def get_single_email(email_id: str, auth_data = Depends(verify_token_with_user_service)):
    """Proxy: Get a specific email by ID"""
    user_data, token = auth_data
    
    try:
        headers = await get_forwarded_headers(token)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{EMAIL_SERVICE_URL}/emails/{email_id}",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Email service unavailable: {str(exc)}")

# 4. SEND EMAIL (FIXED - Now uses Pydantic model)
@router.post("/send")
async def send_email(
    email_request: EmailSendRequest,
    auth_data = Depends(verify_token_with_user_service)
):
    """Proxy: Send an email via the email service"""
    user_data, token = auth_data
    
    try:
        headers = await get_forwarded_headers(token)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{EMAIL_SERVICE_URL}/emails/send",
                headers=headers,
                json=email_request.dict()
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Email service unavailable: {str(exc)}")

# 5. REPLY TO EMAIL (FIXED - Now uses Pydantic model)
@router.post("/{email_id}/reply")
async def reply_to_email(
    email_id: str,
    reply_request: EmailReplyRequest,
    auth_data = Depends(verify_token_with_user_service)
):
    """Proxy: Reply to an email"""
    user_data, token = auth_data
    
    try:
        headers = await get_forwarded_headers(token)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{EMAIL_SERVICE_URL}/emails/{email_id}/reply",
                headers=headers,
                json=reply_request.dict()
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Email service unavailable: {str(exc)}")

# 6. FORWARD EMAIL (FIXED - Now uses Pydantic model)
@router.post("/{email_id}/forward")
async def forward_email(
    email_id: str,
    forward_request: EmailForwardRequest,
    auth_data = Depends(verify_token_with_user_service)
):
    """Proxy: Forward an email"""
    user_data, token = auth_data
    
    try:
        headers = await get_forwarded_headers(token)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{EMAIL_SERVICE_URL}/emails/{email_id}/forward",
                headers=headers,
                json=forward_request.dict()
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Email service unavailable: {str(exc)}")

# 7. MARK EMAIL AS READ
@router.put("/{email_id}/mark-read")
async def mark_email_as_read(email_id: str, auth_data = Depends(verify_token_with_user_service)):
    """Proxy: Mark email as read in both Gmail and database"""
    user_data, token = auth_data
    
    try:
        headers = await get_forwarded_headers(token)
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{EMAIL_SERVICE_URL}/emails/{email_id}/mark-read",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Email service unavailable: {str(exc)}")

# 8. MARK EMAIL AS UNREAD
@router.put("/{email_id}/mark-unread")
async def mark_email_as_unread(email_id: str, auth_data = Depends(verify_token_with_user_service)):
    """Proxy: Mark email as unread in both Gmail and database"""
    user_data, token = auth_data
    
    try:
        headers = await get_forwarded_headers(token)
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{EMAIL_SERVICE_URL}/emails/{email_id}/mark-unread",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Email service unavailable: {str(exc)}")

# 9. UPDATE EMAIL (FIXED - Now uses Pydantic model)
@router.put("/{email_id}/update")
async def update_email(
    email_id: str,
    update_request: EmailUpdateRequest,
    auth_data = Depends(verify_token_with_user_service)
):
    """Proxy: Update email properties in database"""
    user_data, token = auth_data
    
    try:
        headers = await get_forwarded_headers(token)
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{EMAIL_SERVICE_URL}/emails/{email_id}/update",
                headers=headers,
                json=update_request.dict(exclude_unset=True)
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Email service unavailable: {str(exc)}")

# 10. DELETE EMAIL
@router.delete("/{email_id}")
async def delete_email(email_id: str, auth_data = Depends(verify_token_with_user_service)):
    """Proxy: Delete an email by ID"""
    user_data, token = auth_data
    
    try:
        headers = await get_forwarded_headers(token)
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{EMAIL_SERVICE_URL}/emails/{email_id}",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Email service unavailable: {str(exc)}")

# 11. MOVE TO TRASH
@router.put("/{email_id}/trash")
async def move_email_to_trash(email_id: str, auth_data = Depends(verify_token_with_user_service)):
    """Proxy: Move email to trash in Gmail and update database"""
    user_data, token = auth_data
    
    try:
        headers = await get_forwarded_headers(token)
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{EMAIL_SERVICE_URL}/emails/{email_id}/trash",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Email service unavailable: {str(exc)}")

# 12. SEARCH EMAILS (FIXED - Now uses Pydantic model)
@router.post("/search")
async def search_emails(
    search_request: EmailSearchRequest,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    auth_data = Depends(verify_token_with_user_service)
):
    """Proxy: Advanced email search with pagination"""
    user_data, token = auth_data
    
    try:
        headers = await get_forwarded_headers(token)
        params = {
            "skip": skip,
            "limit": limit
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{EMAIL_SERVICE_URL}/emails/search",
                headers=headers,
                json=search_request.dict(exclude_unset=True),
                params=params
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Email service unavailable: {str(exc)}")

# 13. EMAIL STATISTICS
@router.get("/stats/summary")
async def get_email_stats(auth_data = Depends(verify_token_with_user_service)):
    """Proxy: Get email statistics for the user"""
    user_data, token = auth_data
    
    try:
        headers = await get_forwarded_headers(token)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{EMAIL_SERVICE_URL}/emails/stats/summary",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Email service unavailable: {str(exc)}")

# 14. TEST GMAIL CONNECTION
@router.get("/test-gmail-connection")
async def test_gmail_connection(auth_data = Depends(verify_token_with_user_service)):
    """Proxy: Test Gmail API connection for debugging"""
    user_data, token = auth_data
    
    try:
        headers = await get_forwarded_headers(token)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{EMAIL_SERVICE_URL}/emails/test-gmail-connection",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Email service unavailable: {str(exc)}")

# HEALTH CHECK FOR EMAIL SERVICE (No auth needed)
@router.get("/health")
async def email_service_health():
    """Check if email service is healthy"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{EMAIL_SERVICE_URL}/health")
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "email_service_status": response.status_code,
                "service_url": EMAIL_SERVICE_URL
            }
    except httpx.RequestError:
        return {
            "status": "unhealthy",
            "email_service_status": "unavailable",
            "error": "Email service is not reachable",
            "service_url": EMAIL_SERVICE_URL
        }
from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import RedirectResponse
from typing import Optional
import httpx

router = APIRouter(prefix="/auth", tags=["authentication"])

# Configure user service URL - adjust for your deployment
USER_SERVICE_URL = "http://user-service:8000"  # Adjust for your container setup

# Helper function to forward headers if needed
async def get_forwarded_headers(request: Request) -> dict:
    """Extract headers to forward to user service if needed"""
    headers = {}
    # Add any specific headers you want to forward
    if "user-agent" in request.headers:
        headers["user-agent"] = request.headers["user-agent"]
    if "x-forwarded-for" in request.headers:
        headers["x-forwarded-for"] = request.headers["x-forwarded-for"]
    return headers

# 1. LOGIN - Initiate Google OAuth
@router.get("/login")
async def login(request: Request):
    """
    Proxy: Initiate Google OAuth login process.
    Returns the authorization URL that the client should redirect to.
    """
    try:
        headers = await get_forwarded_headers(request)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{USER_SERVICE_URL}/auth/login",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code, 
            detail=exc.response.text
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503, 
            detail=f"User service unavailable: {str(exc)}"
        )

# 2. OAUTH CALLBACK
@router.get("/callback")
async def callback(
    request: Request,
    code: str = Query(..., description="Authorization code from Google"),
    state: str = Query(..., description="State parameter for security")
):
    """
    Proxy: Handle OAuth callback from Google.
    Exchanges authorization code for tokens.
    """
    try:
        headers = await get_forwarded_headers(request)
        params = {
            "code": code,
            "state": state
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{USER_SERVICE_URL}/auth/callback",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code, 
            detail=exc.response.text
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503, 
            detail=f"User service unavailable: {str(exc)}"
        )

# 3. TOKEN VERIFICATION
@router.post("/verify")
async def verify_token(request: Request):
    """
    Proxy: Verify JWT token - used by other microservices.
    Returns user information if token is valid.
    """
    print("\n [DEBUG] this is in gateway user \n")
    try:
        body = await request.json()
        headers = await get_forwarded_headers(request)
  
        headers["content-type"] = "application/json"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{USER_SERVICE_URL}/auth/verify",
                headers=headers,
                json=body
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code, 
            detail=exc.response.text
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503, 
            detail=f"User service unavailable: {str(exc)}"
        )

# 4. GET USER PROFILE BY ID
@router.get("/user/{user_id}")
async def get_user_profile(user_id: str, request: Request):
    """
    Proxy: Get user profile and Google tokens.
    Used by other services that need user's Google OAuth tokens.
    """
    try:
        headers = await get_forwarded_headers(request)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{USER_SERVICE_URL}/auth/user/{user_id}",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code, 
            detail=exc.response.text
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503, 
            detail=f"User service unavailable: {str(exc)}"
        )

# 5. GET USER BY EMAIL
@router.get("/user/email/{email}")
async def get_user_by_email(email: str, request: Request):
    """
    Proxy: Get user by email address.
    Returns basic user information without sensitive data.
    """
    try:
        headers = await get_forwarded_headers(request)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{USER_SERVICE_URL}/auth/user/email/{email}",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code, 
            detail=exc.response.text
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503, 
            detail=f"User service unavailable: {str(exc)}"
        )

# 6. LIST USERS (Admin)
@router.get("/users")
async def list_users(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of users to return")
):
    """
    Proxy: List all users (for admin purposes).
    Returns basic user information without sensitive data.
    """
    try:
        headers = await get_forwarded_headers(request)
        params = {
            "skip": skip,
            "limit": limit
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{USER_SERVICE_URL}/auth/users",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code, 
            detail=exc.response.text
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503, 
            detail=f"User service unavailable: {str(exc)}"
        )

# 7. DELETE USER
@router.delete("/user/{user_id}")
async def delete_user(user_id: str, request: Request):
    """
    Proxy: Delete a user account.
    """
    try:
        headers = await get_forwarded_headers(request)
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{USER_SERVICE_URL}/auth/user/{user_id}",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code, 
            detail=exc.response.text
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503, 
            detail=f"User service unavailable: {str(exc)}"
        )

# 8. HEALTH CHECK FOR USER SERVICE
@router.get("/health")
async def user_service_health():
    """
    Check if user service is healthy and reachable.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{USER_SERVICE_URL}/health")
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "user_service_status": response.status_code,
                "timestamp": response.headers.get("date"),
                "service_url": USER_SERVICE_URL
            }
    except httpx.RequestError as exc:
        return {
            "status": "unhealthy",
            "user_service_status": "unavailable",
            "error": f"User service is not reachable: {str(exc)}",
            "service_url": USER_SERVICE_URL
        }

# 9. LOGOUT (Optional - if you want to add logout functionality)
@router.post("/logout")
async def logout(request: Request):
    """
    Proxy: Logout user (if implemented in user service).
    """
    try:
        # Forward any body content if present
        body = None
        try:
            body = await request.json()
        except:
            pass  # No JSON body
        
        headers = await get_forwarded_headers(request)
        if body:
            headers["content-type"] = "application/json"
        
        async with httpx.AsyncClient() as client:
            if body:
                response = await client.post(
                    f"{USER_SERVICE_URL}/auth/logout",
                    headers=headers,
                    json=body
                )
            else:
                response = await client.post(
                    f"{USER_SERVICE_URL}/auth/logout",
                    headers=headers
                )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            # If logout endpoint doesn't exist, return a generic success
            return {"message": "Logout successful"}
        raise HTTPException(
            status_code=exc.response.status_code, 
            detail=exc.response.text
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503, 
            detail=f"User service unavailable: {str(exc)}"
        )

# 10. GET CURRENT USER (if you have authentication middleware)
@router.get("/me")
async def get_current_user(request: Request):
    """
    Proxy: Get current authenticated user's profile.
    """
    try:
        headers = await get_forwarded_headers(request)
        # Forward authorization header if present
        if "authorization" in request.headers:
            headers["authorization"] = request.headers["authorization"]
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{USER_SERVICE_URL}/auth/me",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            # If /me endpoint doesn't exist, suggest using /user/{id}
            raise HTTPException(
                status_code=404,
                detail="Endpoint not found. Use /auth/user/{user_id} instead."
            )
        raise HTTPException(
            status_code=exc.response.status_code, 
            detail=exc.response.text
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503, 
            detail=f"User service unavailable: {str(exc)}"
        )

# GATEWAY STATUS ENDPOINT
@router.get("/gateway/status")
async def gateway_status():
    """
    Get overall gateway status including connectivity to user service.
    """
    try:
        # Test connection to user service
        async with httpx.AsyncClient(timeout=5.0) as client:
            start_time = httpx._utils.default_ssl_context.time()
            response = await client.get(f"{USER_SERVICE_URL}/health")
            end_time = httpx._utils.default_ssl_context.time()
            response_time = end_time - start_time
            
            return {
                "gateway_status": "operational",
                "user_service": {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time_ms": round(response_time * 1000, 2),
                    "status_code": response.status_code
                },
                "endpoints_available": [
                    "GET /auth/login",
                    "GET /auth/callback", 
                    "POST /auth/verify",
                    "GET /auth/user/{user_id}",
                    "GET /auth/user/email/{email}",
                    "GET /auth/users",
                    "DELETE /auth/user/{user_id}",
                    "GET /auth/health",
                    "POST /auth/logout",
                    "GET /auth/me"
                ]
            }
    except httpx.RequestError:
        return {
            "gateway_status": "degraded", 
            "user_service": {
                "status": "unreachable",
                "error": "Cannot connect to user service"
            },
            "endpoints_available": []
        }
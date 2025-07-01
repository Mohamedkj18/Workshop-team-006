from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from typing import Optional

from services.auth_service import (
    create_authorization_url, 
    exchange_code_for_token, 
    verify_token,
    get_user_by_id,
    get_user_by_email
    ,refresh_token
)
from models.user import (
    Token, 
    TokenVerificationRequest, 
    TokenVerificationResponse,
    User,
    UserWithToken
)

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.get("/login")
async def login():
    """
    Initiate Google OAuth login process.
    Returns the authorization URL that the client should redirect to.
    """
    try:
        auth_url, state = create_authorization_url()
        return {
            "auth_url": auth_url, 
            "state": state,
            "message": "Visit the auth_url to complete login"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create authorization URL: {str(e)}"
        )
    



    

@router.get("/callback")
async def callback(code: str = Query(...), state: str = Query(...)):
    """
    Handle OAuth callback from Google.
    This endpoint receives the authorization code and exchanges it for tokens.
    """
    try:
        access_token, user_id = await exchange_code_for_token(code, state)
        return {
            "access_token": access_token, 
            "token_type": "bearer", 
            "user_id": user_id,
            "message": "Login successful"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to exchange code: {str(e)}"
        )

@router.post("/verify", response_model=TokenVerificationResponse)
async def verify_user_token(request: TokenVerificationRequest):
    """
    Verify JWT token - used by other microservices.
    Returns user information if token is valid.
    """
    print("this is in auth/verify outside", request.token)

    try:
        print("this is in auth/verify", request)
        user_data = await verify_token(request.token)

        return TokenVerificationResponse(
            valid=True, 
            user=user_data
        )
    except Exception as e:
        return TokenVerificationResponse(
            valid=False, 
            error=str(e)
        )
    



@router.post("/refresh", response_model=TokenVerificationResponse)
async def verify_user_token(request: TokenVerificationRequest):
    """
    Verify JWT token - used by other microservices.
    Returns user information if token is valid.
    """
    print("this is in /refresh-token outside", request)

    try:
        print("this is in /refresh", request)
        user_data = await refresh_token(request.token)

        return TokenVerificationResponse(
            valid=True, 
            user=user_data
        )
    except Exception as e:
        return TokenVerificationResponse(
            valid=False, 
            error=str(e)
        )











@router.get("/user/{user_id}", response_model=UserWithToken)
async def get_user_profile(user_id: str):
    """
    Get user profile and Google tokens.
    Used by other services that need user's Google OAuth tokens.
    """
    user = await get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    
    return UserWithToken(**user)

@router.get("/user/email/{email}", response_model=User)
async def get_user_by_email_endpoint(email: str):
    """
    Get user by email address.
    """
    user = await get_user_by_email(email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    
    # Don't return google_token in this endpoint for security
    user_without_token = {k: v for k, v in user.items() if k != 'google_token'}
    return User(**user_without_token)

@router.get("/users")
async def list_users(skip: int = 0, limit: int = 10):
    """
    List all users (for admin purposes).
    Returns basic user information without sensitive data.
    """
    from db.mongodb import get_user_collection
    
    user_collection = get_user_collection()
    
    cursor = user_collection.find(
        {}, 
        {"google_token": 0}  # Exclude sensitive token data
    ).skip(skip).limit(limit)
    
    users = []
    for user in cursor:
        user["id"] = str(user.pop("_id"))
        users.append(User(**user))
    
    return {"users": users, "total": user_collection.count_documents({})}

@router.delete("/user/{user_id}")
async def delete_user(user_id: str):
    """
    Delete a user account.
    """
    from db.mongodb import get_user_collection
    from bson.objectid import ObjectId
    
    user_collection = get_user_collection()
    
    try:
        result = user_collection.delete_one({"_id": ObjectId(user_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from typing import Optional

from app.services.auth_service import create_authorization_url, exchange_code_for_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/login")
async def login():
    """Redirect to Google OAuth consent screen"""
    auth_url, state = create_authorization_url()
    return {"auth_url": auth_url, "state": state}

@router.get("/callback")
async def callback(code: str = Query(...), state: str = Query(...)):
    """Handle OAuth callback from Google"""
    try:
        access_token, user_id = exchange_code_for_token(code, state)
        # In a real app, you might redirect to a frontend with token in query params
        return {"access_token": access_token, "token_type": "bearer", "user_id": user_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to exchange code: {str(e)}"
        )
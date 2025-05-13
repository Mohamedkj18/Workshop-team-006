from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from config import settings
from auth_service import create_authorization_url, exchange_code_for_token

app = FastAPI(title="Auth Service")

# Allow CORS (adjust for prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/auth/login")
async def login():
    """Redirect to Google OAuth consent screen"""
    auth_url, state = create_authorization_url()
    return {"auth_url": auth_url, "state": state}

@app.get("/api/v1/auth/callback")
async def callback(code: str = Query(...), state: str = Query(...)):
    """Handle OAuth callback from Google"""
    try:
        access_token, user_id = exchange_code_for_token(code, state)
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user_id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to exchange code: {str(e)}")

@app.get("/")
def root():
    return {"message": "Auth Service is running"}

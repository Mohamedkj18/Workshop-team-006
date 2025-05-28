from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json
from datetime import datetime, timedelta
from jose import jwt
from bson.objectid import ObjectId
from config import settings
from db.mongodb import get_user_collection

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid'
]

def create_authorization_url():
    """Create Google OAuth authorization URL"""
    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=settings.OAUTH_REDIRECT_URI
    )
    #This line builds the Google login link — the one your frontend will open or redirect the user to.
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'  # Force to get refresh token
    )
    
    return auth_url, state

def exchange_code_for_token(code, state):
    """Exchange authorization code for tokens"""
    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=settings.OAUTH_REDIRECT_URI
    )
    
    # Exchange authorization code for credentials
    flow.fetch_token(code=code)
    credentials = flow.credentials
    
    # Get user info
    user_info = get_user_info(credentials)
    
    # Store user in database
    user_collection = get_user_collection()
    
    # Check if user exists
    existing_user = user_collection.find_one({"email": user_info["email"]})
    
    token_info = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
        "expiry": credentials.expiry.isoformat() if credentials.expiry else None
    }
    
    if existing_user:
        # Update existing user
        user_collection.update_one(
            {"_id": existing_user["_id"]},
            {
                "$set": {
                    "google_token": token_info,
                    "last_login": datetime.utcnow()
                }
            }
        )
        user_id = str(existing_user["_id"])
    else:
        # Create new user
        user_data = {
            "email": user_info["email"],
            "name": user_info["name"],
            "picture": user_info.get("picture"),
            "google_token": token_info,
            "created_at": datetime.utcnow(),
            "last_login": datetime.utcnow()
        }
        
        result = user_collection.insert_one(user_data)
        user_id = str(result.inserted_id)
    
    # Create app access token
    access_token = create_access_token(
        data={"sub": user_info["email"], "user_id": user_id}
    )
    
    return access_token, user_id

def get_user_info(credentials):
    """Get user info from Google"""
    service = build('oauth2', 'v2', credentials=credentials)
    user_info = service.userinfo().get().execute()
    return user_info

def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
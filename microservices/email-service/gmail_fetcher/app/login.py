# Step 1: First, create a file for configuration (config.py)
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Gmail Login API"
    
    # Google OAuth settings
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    
    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-development")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Redirect URI
    OAUTH_REDIRECT_URI: str = os.getenv(
        "OAUTH_REDIRECT_URI", 
        "http://localhost:8000/api/v1/auth/callback"
    )

settings = Settings()

# Step 2: Create database connection (db/mongodb.py)
from pymongo import MongoClient

# Change this to your MongoDB connection string
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["gmail_app"]

user_collection = db["users"]
email_collection = db["emails"]

# Create indexes for better performance
user_collection.create_index("email", unique=True)
email_collection.create_index([("user_id", 1), ("timestamp", -1)])

def get_user_collection():
    return user_collection

def get_email_collection():
    return email_collection

# Step 3: Create models (models/user.py)
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class GoogleToken(BaseModel):
    token: str
    refresh_token: Optional[str] = None
    token_uri: str
    client_id: str
    client_secret: str
    scopes: List[str]
    expiry: str

class User(BaseModel):
    id: str
    email: EmailStr
    name: str
    picture: Optional[str] = None
    google_token: Optional[GoogleToken] = None
    created_at: datetime
    last_login: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str

# Step 4: Create authentication service (services/auth_service.py)
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from jose import jwt
from bson.objectid import ObjectId
import json

from app.config import settings
from app.db.mongodb import get_user_collection

def create_authorization_url():
    """Create Google OAuth authorization URL"""
    flow = Flow.from_client_secrets_file(
        'client_secret.json',  # Download this from Google Cloud Console
        scopes=['https://www.googleapis.com/auth/gmail.readonly', 'openid', 'profile', 'email'],
        redirect_uri=settings.OAUTH_REDIRECT_URI
    )
    
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'  # Force to get refresh token
    )
    
    return auth_url, state

def exchange_code_for_token(code, state):
    """Exchange authorization code for tokens"""
    flow = Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['https://www.googleapis.com/auth/gmail.readonly', 'openid', 'profile', 'email'],
        state=state,
        redirect_uri=settings.OAUTH_REDIRECT_URI
    )
    
    # Exchange authorization code for credentials
    flow.fetch_token(code=code)
    credentials = flow.credentials
    
    # Get user info from Google
    user_info = get_user_info(credentials)
    
    # Store or update user in database
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
    
    # Create app access token (JWT)
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

# Step 5: Create email service (services/email_service.py)
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime
import base64
from bson.objectid import ObjectId

from app.db.mongodb import get_email_collection, get_user_collection

def get_gmail_service(user_id):
    """Get Gmail API service for the user"""
    user_collection = get_user_collection()
    user = user_collection.find_one({"_id": ObjectId(user_id)})
    
    if not user or "google_token" not in user:
        return None
    
    token_info = user["google_token"]
    
    credentials = Credentials(
        token=token_info["token"],
        refresh_token=token_info["refresh_token"],
        token_uri=token_info["token_uri"],
        client_id=token_info["client_id"],
        client_secret=token_info["client_secret"],
        scopes=token_info["scopes"]
    )
    
    return build('gmail', 'v1', credentials=credentials)

def fetch_emails(user_id):
    """Fetch emails for the user"""
    service = get_gmail_service(user_id)
    
    if not service:
        return {"error": "Gmail service not available"}
    
    email_collection = get_email_collection()
    
    try:
        # Get list of messages
        results = service.users().messages().list(
            userId='me', 
            maxResults=20
        ).execute()
        
        messages = results.get('messages', [])
        processed_count = 0
        
        for message in messages:
            # Check if message already exists
            existing = email_collection.find_one({
                "user_id": user_id,
                "message_id": message['id']
            })
            
            if existing:
                continue
            
            msg = service.users().messages().get(
                userId='me', 
                id=message['id'],
                format='full'
            ).execute()
            
            # Extract headers
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
            
            # Extract body
            body = ""
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part.get('mimeType') == 'text/plain':
                        if 'data' in part['body']:
                            body_bytes = base64.urlsafe_b64decode(part['body']['data'])
                            body = body_bytes.decode('utf-8', errors='replace')
                            break
            elif 'body' in msg['payload'] and 'data' in msg['payload']['body']:
                body_bytes = base64.urlsafe_b64decode(msg['payload']['body']['data'])
                body = body_bytes.decode('utf-8', errors='replace')
            
            # Parse timestamp
            internal_date = int(msg['internalDate'])/1000  # Convert to seconds
            timestamp = datetime.fromtimestamp(internal_date)
            
            # Store in database
            email_data = {
                "user_id": user_id,
                "message_id": message['id'],
                "thread_id": msg.get('threadId'),
                "subject": subject,
                "sender": sender,
                "body": body,
                "timestamp": timestamp,
                "read": False
            }
            
            email_collection.insert_one(email_data)
            processed_count += 1
        
        return {"success": True, "processed": processed_count, "total": len(messages)}
        
    except Exception as e:
        return {"error": str(e)}

# Step 6: Create auth routes (routes/auth.py)
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from typing import Optional

from app.services.auth_service import create_authorization_url, exchange_code_for_token
from app.models.user import Token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/login")
async def login():
    """Get Google OAuth authorization URL"""
    auth_url, state = create_authorization_url()
    return {"auth_url": auth_url, "state": state}

@router.get("/callback")
async def callback(code: str = Query(...), state: str = Query(...)):
    """Handle OAuth callback from Google"""
    try:
        access_token, user_id = exchange_code_for_token(code, state)
        # In a real app, you might redirect to a frontend with token in query params
        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=user_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to exchange code: {str(e)}"
        )

# Step 7: Create email routes (routes/emails.py)
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional
from jose import JWTError, jwt
from bson.objectid import ObjectId

from app.config import settings
from app.models.email import Email
from app.services.email_service import fetch_emails
from app.db.mongodb import get_email_collection

# OAuth2 scheme for JWT authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(prefix="/emails", tags=["emails"])

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from JWT token"""
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

@router.get("/")
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
        emails.append(doc)
    
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

# Step 8: Create main application (main.py)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import auth, emails

app = FastAPI(title="Gmail Login & Email Fetcher")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(emails.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to Gmail Login & Email Fetcher API"}
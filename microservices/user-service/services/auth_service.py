from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
from jose import jwt, JWTError
from bson.objectid import ObjectId
from config import settings
import asyncio 

from db.mongodb import get_user_collection


SCOPES = [
    'https://mail.google.com/',
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]

#no await needed because no network or database operations are used here
def create_authorization_url():
    """Create Google OAuth authorization URL"""
    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=settings.OAUTH_REDIRECT_URI
    )
    
    auth_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent'  # Force to get refresh token
    )
    
    return auth_url, state

async def exchange_code_for_token(code, state):
    """Exchange authorization code for tokens (async version)"""
    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=settings.OAUTH_REDIRECT_URI
    )
    
    # Still blocking, must run in a thread
    await asyncio.to_thread(flow.fetch_token, code=code)
    credentials = flow.credentials

    # Already async
    user_info = await get_user_info(credentials)

    user_collection = get_user_collection()  # Should be from AsyncIOMotorClient

    # Check if user exists
    existing_user = await user_collection.find_one({"email": user_info["email"]})

    token_info = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
        "expiry": credentials.expiry.isoformat() if credentials.expiry else None
    }
    print("[DEBUG] SCOPES", credentials.scopes)

    if existing_user:
        await user_collection.update_one(
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
        user_data = {
            "email": user_info["email"],
            "name": user_info["name"],
            "picture": user_info.get("picture"),
            "google_token": token_info,
            "created_at": datetime.utcnow(),
            "last_login": datetime.utcnow()
        }
        result = await user_collection.insert_one(user_data)
        user_id = str(result.inserted_id)

    access_token = create_access_token(
        data={"sub": user_info["email"], "user_id": user_id}
    )

    return access_token, user_id



async def get_user_info(credentials):
    """Get user info from Google (non-blocking using to_thread)"""
    def fetch_userinfo():
        service = build('oauth2', 'v2', credentials=credentials)
        return service.userinfo().get().execute()

    user_info = await asyncio.to_thread(fetch_userinfo)
    return user_info


#NO NEED FOR ASYNC
def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

#NO NEED FOR ASYNC
async def verify_token(token: str):
    """Verify JWT token and return user data"""
    try:
        print("[DEBUG] Verifying token mmmmmmm:", token)
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        print("[DEBUG] AAA", email, user_id)
        if email is None or user_id is None:
            raise JWTError("Invalid token payload")
        
        # Check if user still exists and is active
        user = await get_user_by_id(user_id)
        print("[DEBUG] BBB", "User found" if user else "User not found")
        if not user:
            raise Exception("User not found or has been deleted")
        return {"email": email, "user_id": user_id}
    except JWTError as e:
        raise Exception(f"Invalid token: {str(e)}")



# async def verify_token(token: str):
#     """Verify JWT token and return user data. Auto-refresh if expired."""
#     try:
#         print("[DEBUG] Verifying token:", token,"1111111111111")
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#         email: str = payload.get("sub")
#         user_id: str = payload.get("user_id")
        
#         if email is None or user_id is None:
#             raise JWTError("Invalid token payload")
            
#         return {"email": email, "user_id": user_id}
        
#     except jwt.ExpiredSignatureError:
#         # Token is expired, try to refresh it
#         try:
#             # Decode without verification to get user info
#             payload = jwt.get_unverified_claims(token)
#             user_id = payload.get("user_id")
            
#             if not user_id:
#                 raise Exception("Cannot refresh token: missing user_id")
            
#             # Get user from database to access Google tokens
#             user = await get_user_by_id(user_id)
#             if not user or not user.get("google_token"):
#                 raise Exception("Cannot refresh token: user or Google token not found")
            
#             google_token_info = user["google_token"]
            
#             # Create Google credentials object
#             credentials = Credentials(
#                 token=google_token_info["token"],
#                 refresh_token=google_token_info.get("refresh_token"),
#                 token_uri=google_token_info["token_uri"],
#                 client_id=google_token_info["client_id"],
#                 client_secret=google_token_info["client_secret"],
#                 scopes=google_token_info["scopes"]
#             )
            
#             # Check if Google token is still valid or refresh it
#             if credentials.expired and credentials.refresh_token:
#                 # Refresh the Google token
#                 await asyncio.to_thread(credentials.refresh, Request())
                
#                 # Update the stored Google token in database
#                 updated_token_info = {
#                     "token": credentials.token,
#                     "refresh_token": credentials.refresh_token,
#                     "token_uri": credentials.token_uri,
#                     "client_id": credentials.client_id,
#                     "client_secret": credentials.client_secret,
#                     "scopes": credentials.scopes,
#                     "expiry": credentials.expiry.isoformat() if credentials.expiry else None
#                 }
                
#                 user_collection = get_user_collection()
#                 await user_collection.update_one(
#                     {"_id": ObjectId(user_id)},
#                     {"$set": {"google_token": updated_token_info}}
#                 )
            
#             # Create new JWT token
#             new_access_token = create_access_token(
#                 data={"sub": user["email"], "user_id": user_id}
#             )
#             print("[DEBUG] New access token created:", new_access_token)
#             return {
#                 "email": user["email"], 
#                 "user_id": user_id,
#                 "new_token": new_access_token  # Include new token for client to use
#             }
            
#         except Exception as refresh_error:
#             raise Exception(f"Token expired and refresh failed: {str(refresh_error)}")
            
#     except JWTError as e:
#         raise Exception(f"Invalid token: {str(e)}")
    


async def refresh_token(token: str):
    """Refresh an expired JWT token using stored Google credentials."""
    try:
        print("[DEBUG] Refreshing token:", token)
        
        # Decode without verification to get user info
        payload = jwt.get_unverified_claims(token)
        user_id = payload.get("user_id")
        
        if not user_id:
            raise Exception("Cannot refresh token: missing user_id")
        
        print(f"[DEBUG] Extracting user_id from token: {user_id}")
        
        # Get user from database to access Google tokens
        user = await get_user_by_id(user_id)
        if not user or not user.get("google_token"):
            raise Exception("Cannot refresh token: user or Google token not found")
        
        print(f"[DEBUG] Found user: {user['email']}")
        
        google_token_info = user["google_token"]
        
        # Create Google credentials object
        credentials = Credentials(
            token=google_token_info["token"],
            refresh_token=google_token_info.get("refresh_token"),
            token_uri=google_token_info["token_uri"],
            client_id=google_token_info["client_id"],
            client_secret=google_token_info["client_secret"],
            scopes=google_token_info["scopes"]
        )
        
        print(f"[DEBUG] Google credentials created, expired: {credentials.expired}")
        
        # Check if Google token is still valid or refresh it
        if credentials.expired and credentials.refresh_token:
            print("[DEBUG] Refreshing Google credentials...")
            # Refresh the Google token
            await asyncio.to_thread(credentials.refresh, Request())
            
            # Update the stored Google token in database
            updated_token_info = {
                "token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": credentials.scopes,
                "expiry": credentials.expiry.isoformat() if credentials.expiry else None
            }
            
            user_collection = get_user_collection()
            await user_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"google_token": updated_token_info}}
            )
            print("[DEBUG] Updated Google token in database")
        
        # Create new JWT token
        new_access_token = create_access_token(
            data={"sub": user["email"], "user_id": user_id}
        )
        
        print("[DEBUG] New JWT access token created:", new_access_token)
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "email": user["email"],
            "user_id": user_id,
            "message": "Token refreshed successfully"
        }
        
    except Exception as refresh_error:
        print(f"[DEBUG] Refresh failed: {str(refresh_error)}")
        raise Exception(f"Token refresh failed: {str(refresh_error)}")






async def get_user_by_id(user_id: str):
    """Get user by ID (asynchronously)"""
    try:
        user_collection = get_user_collection()
        user = await user_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            return None
            
        # Convert ObjectId to string
        user["id"] = str(user.pop("_id"))
        return user
    except Exception as e:
        print(f"Error getting user by ID: {str(e)}")
        return None

async def get_user_by_email(email: str):
    """Get user by email"""
    try:
        user_collection = get_user_collection()
        user = await user_collection.find_one({"email": email})
        
        if not user:
            return None
            
        # Convert ObjectId to string
        user["id"] = str(user.pop("_id"))
        return user
    except Exception as e:
        print(f"Error getting user by email: {str(e)}")
        return None


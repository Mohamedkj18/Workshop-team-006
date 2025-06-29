from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, List
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[str] = None

class GoogleToken(BaseModel):
    token: str
    refresh_token: Optional[str] = None
    token_uri: str
    client_id: str
    client_secret: str
    scopes: List[str]
    expiry: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    pass

class UserInDB(UserBase):
    id: str
    picture: Optional[str] = None
    google_token: Optional[GoogleToken] = None
    created_at: datetime
    last_login: Optional[datetime] = None

class User(UserBase):
    id: str
    picture: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None

class UserWithToken(User):
    google_token: Optional[GoogleToken] = None

class TokenVerificationRequest(BaseModel):
    token: str

class TokenVerificationResponse(BaseModel):
    valid: bool
    user: Optional[Dict] = None
    error: Optional[str] = None
    
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, List
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

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
    
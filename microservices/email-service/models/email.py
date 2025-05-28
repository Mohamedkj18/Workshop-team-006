from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class EmailBase(BaseModel):
    subject: str
    sender: str
    recipients: List[str] = []
    body: str
    timestamp: datetime
    read: bool = False

class Email(EmailBase):
    id: str
    user_id: str
    message_id: str
    thread_id: Optional[str] = None
    labels: List[str] = []

class EmailInDB(EmailBase):
    user_id: str
    message_id: str
    thread_id: Optional[str] = None
    labels: List[str] = []

class EmailSendRequest(BaseModel):
    to: List[EmailStr]
    subject: str
    body: str
    cc: Optional[List[EmailStr]] = []
    bcc: Optional[List[EmailStr]] = []

class EmailSendResponse(BaseModel):
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None

class EmailFetchResponse(BaseModel):
    success: bool
    processed: int = 0
    total: int = 0
    error: Optional[str] = None

class EmailUpdateRequest(BaseModel):
    read: Optional[bool] = None

class EmailSearchRequest(BaseModel):
    query: Optional[str] = None
    sender: Optional[str] = None
    subject: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    read: Optional[bool] = None
    labels: Optional[List[str]] = None
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
    to: List[str]  # Changed from EmailStr to str for compatibility
    subject: str
    body: str
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None

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
    labels: Optional[List[str]] = None

class EmailSearchRequest(BaseModel):
    query: Optional[str] = None
    sender: Optional[str] = None
    subject: Optional[str] = None
    from_date: Optional[str] = None  # Keep as string for API compatibility
    to_date: Optional[str] = None    # Keep as string for API compatibility
    read: Optional[bool] = None
    labels: Optional[List[str]] = None

# FIXED - Updated to match the backend service expectations
class EmailReplyRequest(BaseModel):
    reply_body: str                                # Maps to reply_body in backend
    reply_to_all: Optional[bool] = False          # Maps to reply_to_all in backend
    additional_cc: Optional[List[str]] = None     # Maps to additional_cc in backend
    additional_bcc: Optional[List[str]] = None    # Maps to additional_bcc in backend

# FIXED - Updated to match the backend service expectations
class EmailForwardRequest(BaseModel):
    to: List[str]                                 # Maps to to in backend
    forward_message: Optional[str] = ""           # Maps to forward_message in backend
    cc: Optional[List[str]] = None               # Maps to cc in backend
    bcc: Optional[List[str]] = None              # Maps to bcc in backend
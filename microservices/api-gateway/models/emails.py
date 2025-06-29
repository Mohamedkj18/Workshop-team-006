

from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime




class EmailReplyRequest(BaseModel):
    reply_body: str
    reply_to_all: Optional[bool] = False
    additional_cc: Optional[List[str]] = None
    additional_bcc: Optional[List[str]] = None

class EmailForwardRequest(BaseModel):
    to: List[str]
    forward_message: Optional[str] = ""
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None

class EmailSendRequest(BaseModel):
    to: List[str]
    subject: str
    body: str
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None

class EmailUpdateRequest(BaseModel):
    read: Optional[bool] = None
    labels: Optional[List[str]] = None

class EmailSearchRequest(BaseModel):
    query: Optional[str] = None
    sender: Optional[str] = None
    subject: Optional[str] = None
    from_date: Optional[str] = None
    to_date: Optional[str] = None
    labels: Optional[List[str]] = None
    read: Optional[bool] = None

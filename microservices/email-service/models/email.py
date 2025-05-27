from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class Email(BaseModel):
    id: str
    user_id: str
    message_id: str
    thread_id: Optional[str] = None
    subject: str
    sender: str
    recipients: List[str] = []
    body: str
    timestamp: datetime
    read: bool = False
    labels: List[str] = []


class EmailSendRequest(BaseModel):
    to: List[EmailStr]
    subject: str
    body: str
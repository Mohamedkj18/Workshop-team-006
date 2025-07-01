from pydantic import BaseModel

class BufferEmail(BaseModel):
    user_id: str
    email_text: str
    source: str  # "written" or "edited"

class BufferEdit(BaseModel):
    user_id: str
    original_draft: str
    edited_draft: str

class StyleMatchRequest(BaseModel):
    user_id: str
    email_text: str


class EmailReplyRequest(BaseModel):
    user_id: str
    incoming_email: str
    reply_email: str

class EmailRequest(BaseModel):
    user_id: str
    email_text: str

class StyleVectorResponse(BaseModel):
    derived_labels: dict

class InitUserStyleRequest(BaseModel):
    user_id: str
    emails: list[str]


class InitUserReplyStyleRequest(BaseModel):
    user_id: str
    emails_replies: list[list[str]]

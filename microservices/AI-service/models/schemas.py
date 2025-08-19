from pydantic import BaseModel

class EmailPrompt(BaseModel):
    user_id: str
    prompt: str

class ReplyRequest(BaseModel):
    user_id: str
    email_body: str
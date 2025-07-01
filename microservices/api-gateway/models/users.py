
from pydantic import BaseModel

class TokenVerificationRequest(BaseModel):
    token: str
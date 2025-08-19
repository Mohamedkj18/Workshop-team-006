from fastapi import APIRouter, HTTPException
from models.schemas import EmailPrompt
from services.email_generation import generate_email

router = APIRouter()

@router.post("/generate-email")
def generate_email_route(prompt: EmailPrompt):
    try:
        result = generate_email(prompt.user_id, prompt.prompt)
        return {"body": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
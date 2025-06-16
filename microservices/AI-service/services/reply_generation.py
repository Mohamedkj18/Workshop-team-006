from fastapi import APIRouter, HTTPException
from models.schemas import ReplyRequest
from services.reply_generation import generate_reply

router = APIRouter()

@router.post("/generate-reply")
def generate_reply_route(request: ReplyRequest):
    try:
        result = generate_reply(request.user_id, request.email_body)
        return {"reply": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
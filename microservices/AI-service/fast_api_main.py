from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ai_utils import generate_email, generate_reply

app = FastAPI()

class EmailPrompt(BaseModel):
    prompt: str

@app.post("/generate-email")
def generate_email_route(prompt: EmailPrompt):
    try:
        result = generate_email(prompt.prompt)
        return {"email": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ReplyRequest(BaseModel):
    email_body: str

@app.post("/generate-reply")
def generate_reply_route(request: ReplyRequest):
    try:
        result = generate_reply(request.email_body)
        return {"reply": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

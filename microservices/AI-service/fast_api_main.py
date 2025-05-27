from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from style_learning import learn_user_style
from typing import List
from ai_utils import generate_email, generate_reply

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 👈 In dev, this allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EmailPrompt(BaseModel):
    user_id: str
    prompt: str

@app.post("/generate-email")
def generate_email_route(prompt: EmailPrompt):
    print(f"📩 Received prompt: {prompt.prompt}")
    try:
        result = generate_email(prompt.prompt)
        print(f"✅ Generated result: {result}")
        return {"body": result}
    except Exception as e:
        print(f"❌ Exception in generate_email: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class ReplyRequest(BaseModel):
    user_id: str
    email_body: str

@app.post("/generate-reply")
def generate_reply_route(request: ReplyRequest):
    try:
        result = generate_reply({
            "user_id": request.user_id,
            "body": request.email_body
        })
        return {"reply": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class StyleLearnRequest(BaseModel):
    user_id: str
    emails: List[dict] 


@app.post("/learn-style")
def learn_style_route(request: StyleLearnRequest):
    try:
        tone, length, complexity = learn_user_style(request.user_id, request.emails)
        return {
            "user_id": request.user_id,
            "style": {
                "tone": tone,
                "length": length,
                "complexity": complexity
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

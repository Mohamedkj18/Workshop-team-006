from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import httpx
from typing import List

router = APIRouter(tags=["AI"])
AI_SERVICE_URL = "http://ai-service:8001"

class EmailBody(BaseModel):
    body: str

class StyleLearnRequest(BaseModel):
    user_id: str
    emails: List[dict] 


class EmailPrompt(BaseModel):
    user_id: str
    prompt: str

class ReplyRequest(BaseModel):
    user_id: str
    email_body: str


@router.post("/ai/generate-email")
async def generate_email_route(payload: EmailPrompt):
    try:
        print(f"→ Forwarding to: {AI_SERVICE_URL}/generate-email")
        print(f"→ Payload: {payload.dict()}")
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"{AI_SERVICE_URL}/generate-email",
                json=payload.dict()
            )
            print(f"✅ Response status: {response.status_code}")
            print(f"✅ Response body: {response.text}")
            response.raise_for_status()
            return response.json()

    except httpx.RequestError as e:
        print(f"❌ RequestError: {e}")
        raise HTTPException(status_code=503, detail=f"AI service unreachable: {e}")

    except httpx.HTTPStatusError as e:
        print(f"❌ HTTPStatusError: {e}")
        print(f"📄 Response text: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"AI error: {e.response.text}")

    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error contacting AI service.")

@router.post("/ai/generate-reply")
async def generate_reply_route(payload: ReplyRequest):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{AI_SERVICE_URL}/generate-reply", json=payload.dict())
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"AI service unreachable: {e}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"AI error: {e.response.text}")

@router.post("/ai/learn-style")
async def learn_style_route(payload: StyleLearnRequest):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{AI_SERVICE_URL}/learn-style", json=payload.dict())
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"AI service unreachable: {e}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"AI error: {e.response.text}")

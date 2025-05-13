from fastapi import APIRouter, HTTPException, Request
import httpx

router = APIRouter()
AI_SERVICE_URL = "http://ai-service:5001"  

@router.post("/ai/generate-reply")
async def generate_reply(request: Request):
    try:
        data = await request.json()
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{AI_SERVICE_URL}/generate-reply", json=data)
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"AI service unreachable: {e}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"AI error: {e.response.text}")

@router.post("/ai/generate-email")
async def generate_email(request: Request):
    try:
        data = await request.json()
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{AI_SERVICE_URL}/generate-email", json=data)
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"AI service unreachable: {e}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"AI error: {e.response.text}")
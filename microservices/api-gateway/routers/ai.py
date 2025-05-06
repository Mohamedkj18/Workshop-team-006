from fastapi import APIRouter, Request
import httpx

router = APIRouter()

@router.post("/generate-reply")
async def generate_reply(req: Request):
    # Step 1: Read incoming request body
    payload = await req.json()

    # Step 2: Forward request to AI-service
    async with httpx.AsyncClient() as client:
        response = await client.post("http://AI-service:5000/generate", json=payload)

    # Step 3: Return AI-service response back to caller
    return response.json()
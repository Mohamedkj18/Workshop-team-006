from fastapi import APIRouter, Request, HTTPException
import httpx

router = APIRouter()
AUTH_SERVICE_URL = "http://auth-service:8000/api/v1/auth"  # adjust if needed

@router.post("/auth/google")
async def login_with_google(request: Request):
    """Login using Google OAuth"""
    body = await request.json()
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{AUTH_SERVICE_URL}/google", json=body)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
        return response.json()

'''@router.get("/auth/validate")
async def validate_token(token: str):
    """Validate auth token"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{AUTH_SERVICE_URL}/validate", params={"token": token})
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
        return response.json()'''

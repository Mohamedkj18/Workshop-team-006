from fastapi import APIRouter, Request, HTTPException
import httpx

router = APIRouter()
AUTH_SERVICE_URL = "http://auth-service:8003"

@router.post("/auth/google")
async def login(request: Request):
    """Login using Google OAuth"""
    body = await request.json()
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{AUTH_SERVICE_URL}/api/v1/auth/login", json=body)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
        return response.json()

#mohamed addition:
@router.get("/login")
async def login():
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{AUTH_SERVICE_URL}/api/v1/auth/login")
            return res.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Auth service error: {e}")

@router.get("/callback")
async def callback(code: str, state: str):
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{AUTH_SERVICE_URL}/api/v1/auth/callback", params={"code": code, "state": state})
            return res.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Auth service error: {e}")
    
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

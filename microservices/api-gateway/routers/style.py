from fastapi import APIRouter, HTTPException
import httpx
from models import shcemas

router = APIRouter(prefix="/api/style")

SERVICE_URL = "http://user-style-service:8010"

# POST /api/style/add-to-buffer
@router.post("/add-to-buffer")
async def add_to_buffer(req: shcemas.BufferEmail):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{SERVICE_URL}/buffer/add-to-buffer", json=req.dict())
            return response.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="User style service unreachable")

# POST /api/style/init-user-style → /style/init-user-style
@router.post("/init-user-style")
async def init_user_style(req: shcemas.InitUserStyleRequest):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{SERVICE_URL}/style/init-user-style", json=req.dict())
            return response.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="User style service unreachable")

# POST /api/style/update-user-general-style → /style/update
@router.post("/update-user-general-style")
async def update_user_general_style(req: shcemas.EmailRequest):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{SERVICE_URL}/style/update-user-general-style", json=req.dict())
            return response.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="User style service unreachable")

# POST /api/style/get-user-general-style → /style/get
@router.post("/get-user-general-style")
async def get_user_general_style(req: shcemas.EmailRequest):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{SERVICE_URL}/style/get-user-general-style", json=req.dict())
            return response.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="User style service unreachable")

# POST /api/style/reply/init-user-style → /reply/init-reply-clusters
@router.post("/reply/init-user-style")
async def init_user_reply_style(req: shcemas.InitUserReplyStyleRequest):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{SERVICE_URL}/reply/init-user-style", json=req.dict())
            return response.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="User style service unreachable")

# POST /api/style/reply/update-user-reply-style → /reply/update
@router.post("/reply/update-user-reply-style")
async def update_user_reply_style(req: shcemas.EmailReplyRequest):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{SERVICE_URL}/reply/update-user-reply-style", json=req.dict())
            return response.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="User style service unreachable")

# POST /api/style/reply/get-user-reply-style → /reply/get-style
@router.post("/reply/get-user-reply-style")
async def get_user_reply_style(req: shcemas.EmailReplyRequest):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{SERVICE_URL}/reply/get-user-reply-style", json=req.dict())
            return response.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="User style service unreachable")
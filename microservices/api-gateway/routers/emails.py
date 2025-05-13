from fastapi import APIRouter, Request, HTTPException
import httpx

router = APIRouter()
EMAIL_SERVICE_URL = "http://email-service/gmail_fetcher/app/:8000"  # Adjust for container or host setup

@router.post("/email/send")
async def send_email(request: Request):
    """Proxy: Send an email via the internal email service"""
    body = await request.json()
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{EMAIL_SERVICE_URL}/email/send", json=body)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)


@router.get("/emails")
async def list_emails():
    """Proxy: List emails via the internal email service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{EMAIL_SERVICE_URL}/emails")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)


@router.get("/email/{email_id}")
async def get_email(email_id: str):
    """Proxy: Get a specific email by ID"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{EMAIL_SERVICE_URL}/email/{email_id}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)


@router.delete("/email/{email_id}")
async def delete_email(email_id: str):
    """Proxy: Delete an email by ID"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{EMAIL_SERVICE_URL}/email/{email_id}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)


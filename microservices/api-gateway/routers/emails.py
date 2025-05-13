from fastapi import APIRouter, Request, HTTPException
import httpx

router = APIRouter()
EMAIL_SERVICE_URL = "http://email-service:8002"

# --- Send Email (if supported by email-service) ---
@router.post("/emails/send")
async def send_email(request: Request):
    """Proxy: Send an email (if supported by internal service)"""
    body = await request.body()
    headers = {"Authorization": request.headers.get("Authorization", "")}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{EMAIL_SERVICE_URL}/api/v1/emails/send", content=body, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)

# --- List Emails ---
@router.get("/emails")
async def list_emails(request: Request):
    headers = {"Authorization": request.headers.get("Authorization", "")}
    params = dict(request.query_params)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{EMAIL_SERVICE_URL}/api/v1/emails", headers=headers, params=params)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)

# --- Get Email by ID ---
@router.get("/emails/{email_id}")
async def get_email(email_id: str, request: Request):
    headers = {"Authorization": request.headers.get("Authorization", "")}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{EMAIL_SERVICE_URL}/api/v1/emails/{email_id}", headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)

# --- Delete Email by ID (if supported) ---
@router.delete("/emails/{email_id}")
async def delete_email(email_id: str, request: Request):
    headers = {"Authorization": request.headers.get("Authorization", "")}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{EMAIL_SERVICE_URL}/api/v1/emails/{email_id}", headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)

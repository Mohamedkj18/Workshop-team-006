from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/emails/inbox")
async def get_inbox():
    """Get inbox emails"""
    pass

@router.get("/emails/sent")
async def get_sent():
    """Get sent emails"""
    pass

@router.get("/emails/trash")
async def get_trash():
    """Get trashed/deleted emails"""
    pass

@router.get("/emails/{email_id}")
async def get_email(email_id: str):
    """Get full email details by ID"""
    pass

@router.post("/emails/send")
async def send_email(request: Request):
    """Send a new email"""
    pass

@router.delete("/emails/{email_id}")
async def delete_email(email_id: str):
    """Move email to trash"""
    pass

from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/drafts")
async def get_all_drafts():
    """Get all drafts for the authenticated user"""
    pass

@router.get("/drafts/{draft_id}")
async def get_draft(draft_id: str):
    """Get a specific draft by ID"""
    pass

@router.post("/drafts")
async def create_draft(request: Request):
    """Create a new draft"""
    pass

@router.put("/drafts/{draft_id}")
async def update_draft(draft_id: str, request: Request):
    """Update an existing draft by ID"""
    pass

@router.delete("/drafts/{draft_id}")
async def delete_draft(draft_id: str):
    """Delete a draft by ID"""
    pass

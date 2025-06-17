from fastapi import APIRouter, BackgroundTasks
from models.schemas import BufferEmail
from services.buffer_handler import add_to_buffer, check_and_learn


router = APIRouter()

@router.post("/buffer/add-to-buffer")
def receive_buffer(request: BufferEmail, background_tasks: BackgroundTasks):
    add_to_buffer(request.user_id, request.email_text, request.source)
    background_tasks.add_task(check_and_learn, request.user_id)
    return {"status": "buffered"}

@router.get("/buffer/ping")
def ping_buffer():
    return {"status": "buffer online"}
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.database import SessionLocal
from db.models import LearningProfile
from services.style_updater import update_learning_profile, learn_user_style
from models.schemas import EmailRequest, StyleVectorResponse, InitUserStyleRequest

router = APIRouter()


@router.post("/style/init-user-style")
def init_user_style(req: InitUserStyleRequest):
    labels, vector = learn_user_style(req.user_id, req.emails)
    return {
        "vector": vector,
        "derived_labels": labels
    }

@router.post("/style/update-user-general-style", response_model=StyleVectorResponse)
def update_user_style(req: EmailRequest):
    update_learning_profile(req.user_id, req.email_text)
    db = SessionLocal()
    profile = db.query(LearningProfile).filter_by(user_id=req.user_id).first()
    db.close()
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    return {"derived_labels": profile.derived_labels}

@router.post("/style/get-user-general-style", response_model=StyleVectorResponse)
def get_user_style(req: EmailRequest):
    db = SessionLocal()
    profile = db.query(LearningProfile).filter_by(user_id=req.user_id).first()
    db.close()
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    return {"derived_labels": profile.derived_labels}
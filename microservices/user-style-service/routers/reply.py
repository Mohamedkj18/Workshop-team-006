from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.database import SessionLocal
from db.models import StyleCluster
from services.reply_updater import update_reply_style_vector
from services.feature_extraction import extract_features_from_emails
from utils.similarity import cosine_similarity
import numpy as np
from models.schemas import EmailRequest, EmailReplyRequest


router = APIRouter()


@router.post("/reply/update-user-reply-style", response_model=dict)
def update_reply_style(req: EmailReplyRequest):
    success = update_reply_style_vector(req.user_id, req.incoming_email, req.reply_email)
    if not success:
        raise HTTPException(status_code=400, detail="Could not update reply style")
    return {"status": "updated"}

@router.post("/reply/get-user-reply-style", response_model=dict)
def get_reply_style_vector(req: EmailRequest):
    db = SessionLocal()
    clusters = db.query(StyleCluster).filter_by(user_id=req.user_id).all()
    db.close()

    if not clusters:
        raise HTTPException(status_code=404, detail="No reply clusters found for user")

    input_vec = list(extract_features_from_emails([req.email_text]).values())
    similarities = [cosine_similarity(input_vec, cluster.centroid_vector) for cluster in clusters]
    best_idx = int(np.argmax(similarities))
    best_cluster = clusters[best_idx]

    return {"reply_style_vector": best_cluster.reply_style_vector}

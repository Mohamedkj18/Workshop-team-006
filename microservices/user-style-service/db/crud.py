from sqlalchemy.orm import Session
from db.models import LearningProfile
from datetime import datetime

def get_user_profile(db: Session, user_id: str):
    return db.query(LearningProfile).filter_by(user_id=user_id).first()

def upsert_learning_profile(db: Session, user_id: str, feature_vector: dict, labels: dict, count: int):
    existing = get_user_profile(db, user_id)
    if existing:
        existing.feature_vector = feature_vector
        existing.derived_labels = labels
        existing.email_count = count
        existing.last_updated = datetime.utcnow()
    else:
        new_entry = LearningProfile(
            user_id=user_id,
            feature_vector=feature_vector,
            derived_labels=labels,
            email_count=count,
            last_updated=datetime.utcnow()
        )
        db.add(new_entry)
    db.commit()
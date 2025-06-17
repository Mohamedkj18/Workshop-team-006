from db.database import SessionLocal
from db.models import StyleEmailBuffer
from db.crud import get_user_profile
from services.style_updater import update_learning_profile

def add_to_buffer(user_id: str, email_text: str, source: str):
    db = SessionLocal()
    entry = StyleEmailBuffer(user_id=user_id, email_text=email_text, source=source)
    db.add(entry)
    db.commit()
    db.close()

def check_and_learn(user_id: str, threshold: int = 5):
    db = SessionLocal()
    emails = db.query(StyleEmailBuffer).filter_by(user_id=user_id).order_by(StyleEmailBuffer.created_at).all()

    if len(emails) >= threshold:
        for e in emails:
            update_learning_profile(user_id, e.email_text)
            db.delete(e)
        db.commit()

    db.close()

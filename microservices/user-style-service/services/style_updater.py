from db.database import SessionLocal
from db.crud import upsert_learning_profile
from db.models import LearningProfile
from services.feature_extraction import extract_features_from_emails

def generate_derived_labels(vector: dict) -> dict:
    return {
        "tone": "friendly" if vector["polarity_mean"] > 0.2 else "neutral",
        "length": "concise" if vector["avg_sentence_length"] < 12 else "detailed",
        "complexity": "advanced" if vector["reading_grade_level"] > 10 else "moderate",
        "formality": "formal" if vector["passive_voice_ratio"] > 0.1 else "informal",
        "processing_style": "sequential" if vector["question_ratio"] < 0.05 else "inquisitive"
    }

def learn_user_style(user_id: str, emails: list):
    db = SessionLocal()
    email_texts = [e["body"] if isinstance(e, dict) and "body" in e else str(e) for e in emails]
    vector = extract_features_from_emails(email_texts)
    labels = generate_derived_labels(vector)
    upsert_learning_profile(db, user_id, vector, labels, len(email_texts))
    db.close()
    return labels, vector

def update_learning_profile(user_id: str, email_text: str):
    db = SessionLocal()
    vector = extract_features_from_emails([email_text])

    profile = db.query(LearningProfile).filter_by(user_id=user_id).first()
    if not profile:
        # If no profile exists, treat it as initial learning
        labels = generate_derived_labels(vector)
        upsert_learning_profile(db, user_id, vector, labels, 1)
    else:
        old_vector = profile.vector or {}
        count = profile.sample_count or 0

        # Update vector via weighted average
        new_vector = {}
        for key in vector:
            prev = old_vector.get(key, 0)
            new_vector[key] = round((prev * count + vector[key]) / (count + 1), 3)

        labels = generate_derived_labels(new_vector)
        upsert_learning_profile(db, user_id, new_vector, labels, count + 1)

    db.close()
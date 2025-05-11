## note: this maybe added to user.py in models/, and 

class WritingStyle(BaseModel):
    avg_sentence_length: float = 0.0
    vocabulary_diversity: float = 0.0
    formality_score: float = 0.0
    common_phrases: List[str] = []
    greeting_style: Optional[str] = None
    closing_style: Optional[str] = None
    emoji_usage: float = 0.0
    exclamation_usage: float = 0.0
    question_usage: float = 0.0
    last_updated: datetime = datetime.utcnow()

from sqlalchemy import Column, String, Integer, JSON, Text, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class LearningProfile(Base):
    __tablename__ = "learning_profiles"
    user_id = Column(String, primary_key=True)
    feature_vector = Column(JSON, nullable=False)
    derived_labels = Column(JSON, nullable=True)
    email_count = Column(Integer, default=0, nullable=False)
    last_updated = Column(TIMESTAMP, server_default=func.now(), nullable=False)

class LearningProfileVersion(Base):
    __tablename__ = "learning_profile_versions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False)
    feature_vector = Column(JSON, nullable=False)
    derived_labels = Column(JSON, nullable=True)
    email_count = Column(Integer, nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

class StyleEmailBuffer(Base):
    __tablename__ = "style_email_buffer"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False)
    email_text = Column(Text, nullable=False)
    source = Column(String, nullable=False)  # "written" or "edited"
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
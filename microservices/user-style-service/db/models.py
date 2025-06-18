from sqlalchemy import Column, String, Integer, JSON, Text, TIMESTAMP, func, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime


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


class StyleCluster(Base):
    __tablename__ = "style_clusters"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False)
    cluster_id = Column(Integer, nullable=False)
    centroid_vector = Column(JSON, nullable=False)
    reply_style_vector = Column(JSON, nullable=True)
    sample_count = Column(Integer, default=0)


class EmailReplyPair(Base):
    __tablename__ = "email_reply_pairs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    incoming_email = Column(Text)
    reply_email = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class ClusterStatus(Base):
    __tablename__ = "cluster_status"
    user_id = Column(String, primary_key=True)
    pair_count_since_last_cluster = Column(Integer, default=0)


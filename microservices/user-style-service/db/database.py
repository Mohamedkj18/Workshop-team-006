from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

DATABASE_URL = "postgresql+psycopg2://postgres:style123@style-db:5432/style-db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__=="__main__":
    init_db()
    print("Database initalized successfully")
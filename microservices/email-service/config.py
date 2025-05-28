from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Email Service"
    
    # MongoDB settings
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB: str = os.getenv("MONGO_DB", "email_service_db")
    
    # User service URL
    USER_SERVICE_URL: str = os.getenv("USER_SERVICE_URL", "http://user-service:8003")
    
    # Email fetching settings
    EMAIL_FETCH_BATCH_SIZE: int = int(os.getenv("EMAIL_FETCH_BATCH_SIZE", "20"))
    EMAIL_FETCH_TIMEOUT: int = int(os.getenv("EMAIL_FETCH_TIMEOUT", "30"))

settings = Settings()
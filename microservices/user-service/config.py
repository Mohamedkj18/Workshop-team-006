from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "User Authentication Service"
    
    # MongoDB settings
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB: str = os.getenv("MONGO_DB", "user_service_db")
    
    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-development")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Google OAuth settings
    GOOGLE_CLIENT_SECRETS_FILE: str = os.getenv("GOOGLE_CLIENT_SECRETS_FILE", "client_secret.json")
    OAUTH_REDIRECT_URI: str = os.getenv(
        "OAUTH_REDIRECT_URI", 
        "http://localhost:8003/api/v1/auth/callback"
    )

settings = Settings()
from pydantic_settings  import BaseSettings
import os

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Email Service"

    # MongoDB
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB: str = os.getenv("MONGO_DB", "gmail_app")

    # JWT verification
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key")
    ALGORITHM: str = "HS256"

settings = Settings()

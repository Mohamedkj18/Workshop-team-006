from pymongo import MongoClient
from config import settings
from motor.motor_asyncio import AsyncIOMotorClient

# Initialize MongoDB client
client = AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.MONGO_DB]

# Collections
email_collection = db["emails"]

# Create indexes for better performance
email_collection.create_index([("user_id", 1), ("timestamp", -1)])
email_collection.create_index([("user_id", 1), ("message_id", 1)], unique=True)
email_collection.create_index([("user_id", 1), ("read", 1)])
email_collection.create_index([("user_id", 1), ("sender", 1)])

def get_email_collection():
    """Get email collection"""
    return email_collection

def get_database():
    """Get database instance"""
    return db

def close_db_connection():
    """Close database connection"""
    client.close()
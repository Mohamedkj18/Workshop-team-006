from pymongo import MongoClient
from config import settings

# Initialize MongoDB client
client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB]

# Collections
user_collection = db["users"]

# Create indexes
user_collection.create_index("email", unique=True)

def get_user_collection():
    """Get user collection"""
    return user_collection

def get_database():
    """Get database instance"""
    return db

def close_db_connection():
    """Close database connection"""
    client.close()
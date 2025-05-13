from pymongo import MongoClient
from config import settings

client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB]

user_collection = db["users"]
email_collection = db["emails"]

# Create indexes
user_collection.create_index("email", unique=True)
email_collection.create_index([("user_id", 1), ("timestamp", -1)])

def get_user_collection():
    return user_collection

def get_email_collection():
    return email_collection
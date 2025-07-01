"""
database.py

This module is responsible for configuring and establishing a connection to the MongoDB database.
It uses the `pymongo` library to connect to a MongoDB cluster and provides access to the 
'draft_collection' within the 'draft_db' database.

Variables:
- MONGO_USERNAME: The username for MongoDB authentication.
- MONGO_PASSWORD: The password for MongoDB authentication.
- uri: The connection string used to connect to the MongoDB cluster.
- client: The MongoDB client instance.
- db: The database instance for 'draft_db'.
- drafts_collection: The collection instance for 'draft_collection'.
"""

from pymongo                import MongoClient
from os                     import getenv
from pymongo.server_api     import ServerApi

# my modules
from logger.loggers         import root_logger

#connect to mongoDB
DRAFTS_MONGO_USERNAME = getenv("DRAFTS_MONGO_USERNAME")
DRAFTS_MONGO_PASSWORD = getenv("DRAFTS_MONGO_PASSWORD")
uri = f"mongodb+srv://{DRAFTS_MONGO_USERNAME}:{DRAFTS_MONGO_PASSWORD}@cluster0.79pz2ce.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    root_logger.info("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    root_logger.error(f"MongoDB connection failed: {e}")

# connect to the drafts database
db = client.draft_db
drafts_collection = db['draft_collection']
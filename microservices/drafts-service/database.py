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

from pymongo import MongoClient

MONGO_USERNAME = "abomokh"
MONGO_PASSWORD = "UhU86crgAotnAz5W"
uri = f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@cluster0.79pz2ce.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)

db = client.draft_db
drafts_collection = db['draft_collection']
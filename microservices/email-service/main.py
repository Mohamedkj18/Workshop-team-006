from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional
from jose import JWTError, jwt
from bson.objectid import ObjectId
from datetime import datetime

from config import settings
from email_service import fetch_emails
from pymongo import MongoClient

# Setup DB access (in-memory or shared)
client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB]
email_collection = db["emails"]

# App + CORS
app = FastAPI(title="Email Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        if email is None or user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return {"email": email, "user_id": user_id}

# Routes
@app.post("/api/v1/emails/fetch")
async def fetch_user_emails(current_user=Depends(get_current_user)):
    return fetch_emails(current_user["user_id"])

@app.get("/api/v1/emails")
async def get_emails(
    skip: int = 0,
    limit: int = 20,
    read: Optional[bool] = None,
    current_user=Depends(get_current_user)
):
    query = {"user_id": current_user["user_id"]}
    if read is not None:
        query["read"] = read
    cursor = email_collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)

    emails = []
    for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        emails.append(doc)
    return emails

@app.put("/api/v1/emails/{email_id}/read")
async def mark_email_as_read(email_id: str, read: bool = True, current_user=Depends(get_current_user)):
    try:
        result = email_collection.update_one(
            {"_id": ObjectId(email_id), "user_id": current_user["user_id"]},
            {"$set": {"read": read}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Email not found")
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
def root():
    return {"message": "Email Service is running"}

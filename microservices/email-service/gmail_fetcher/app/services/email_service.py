from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from bson.objectid import ObjectId
import base64
from email.mime.text import MIMEText
from datetime import datetime

from app.db.mongodb import get_email_collection, get_user_collection

def get_gmail_service(user_id):
    """Get Gmail API service for the user"""
    user_collection = get_user_collection()
    user = user_collection.find_one({"_id": ObjectId(user_id)})
    
    if not user or "google_token" not in user:
        return None
    
    token_info = user["google_token"]
    
    credentials = Credentials(
        token=token_info["token"],
        refresh_token=token_info["refresh_token"],
        token_uri=token_info["token_uri"],
        client_id=token_info["client_id"],
        client_secret=token_info["client_secret"],
        scopes=token_info["scopes"]
    )
    
    return build('gmail', 'v1', credentials=credentials)

def fetch_emails(user_id):
    """Fetch emails for the user"""
    service = get_gmail_service(user_id)
    
    if not service:
        return {"error": "Gmail service not available"}
    
    email_collection = get_email_collection()
    
    try:
        # Get list of messages
        results = service.users().messages().list(
            userId='me', 
            maxResults=20
        ).execute()
        
        messages = results.get('messages', [])
        processed_count = 0
        
        for message in messages:
            # Check if message already exists
            existing = email_collection.find_one({
                "user_id": user_id,
                "message_id": message['id']
            })
            
            if existing:
                continue
            
            msg = service.users().messages().get(
                userId='me', 
                id=message['id'],
                format='full'
            ).execute()
            
            # Extract headers
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
            
            # Extract recipients
            to_header = next((h['value'] for h in headers if h['name'].lower() == 'to'), '')
            recipients = [r.strip() for r in to_header.split(',')] if to_header else []
            
            # Extract body
            body = ""
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part.get('mimeType') == 'text/plain':
                        if 'data' in part['body']:
                            body_bytes = base64.urlsafe_b64decode(part['body']['data'])
                            body = body_bytes.decode('utf-8', errors='replace')
                            break
            elif 'body' in msg['payload'] and 'data' in msg['payload']['body']:
                body_bytes = base64.urlsafe_b64decode(msg['payload']['body']['data'])
                body = body_bytes.decode('utf-8', errors='replace')
            
            # Parse timestamp
            internal_date = int(msg['internalDate'])/1000  # Convert to seconds
            timestamp = datetime.fromtimestamp(internal_date)
            
            # Get labels
            labels = msg.get('labelIds', [])
            
            # Store in database
            email_data = {
                "user_id": user_id,
                "message_id": message['id'],
                "thread_id": msg.get('threadId'),
                "subject": subject,
                "sender": sender,
                "recipients": recipients,
                "body": body,
                "timestamp": timestamp,
                "read": 'UNREAD' not in labels,
                "labels": labels
            }
            
            email_collection.insert_one(email_data)
            processed_count += 1
        
        return {"success": True, "processed": processed_count}
        
    except Exception as e:
        return {"error": str(e)}
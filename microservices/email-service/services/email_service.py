from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from bson.objectid import ObjectId
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Optional, Dict

from db.mongodb import get_email_collection
from services.user_service_client import user_service_client
from config import settings

class EmailService:
    """Service for handling email operations"""
    
    def __init__(self):
        self.email_collection = get_email_collection()
    
    async def get_gmail_service(self, user_id: str):
        """Get Gmail API service for the user"""
        # Get user's Google token from user service
        user_data = await user_service_client.get_user_profile(user_id)
        
        if not user_data or not user_data.get("google_token"):
            return None
        
        token_info = user_data["google_token"]
        
        try:
            credentials = Credentials(
                token=token_info["token"],
                refresh_token=token_info.get("refresh_token"),
                token_uri=token_info["token_uri"],
                client_id=token_info["client_id"],
                client_secret=token_info["client_secret"],
                scopes=token_info["scopes"]
            )
            
            return build('gmail', 'v1', credentials=credentials)
        except Exception as e:
            print(f"Error creating Gmail service: {str(e)}")
            return None
    
    async def fetch_emails(self, user_id: str) -> Dict:
        """Fetch emails for the user from Gmail API"""
        service = await self.get_gmail_service(user_id)
        
        if not service:
            return {"success": False, "error": "Gmail service not available"}
        
        try:
            # Get list of messages
            results = service.users().messages().list(
                userId='me', 
                maxResults=settings.EMAIL_FETCH_BATCH_SIZE
            ).execute()
            
            messages = results.get('messages', [])
            processed_count = 0
            
            for message in messages:
                # Check if message already exists
                existing = self.email_collection.find_one({
                    "user_id": user_id,
                    "message_id": message['id']
                })
                
                if existing:
                    continue
                
                # Get full message details
                msg = service.users().messages().get(
                    userId='me', 
                    id=message['id'],
                    format='full'
                ).execute()
                
                # Parse and store email
                email_data = self._parse_email_message(msg, user_id)
                if email_data:
                    self.email_collection.insert_one(email_data)
                    processed_count += 1
            
            return {
                "success": True, 
                "processed": processed_count,
                "total": len(messages)
            }
            
        except HttpError as e:
            return {"success": False, "error": f"Gmail API error: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
    
    def _parse_email_message(self, msg: Dict, user_id: str) -> Optional[Dict]:
        """Parse Gmail API message format into our email format"""
        try:
            # Extract headers
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
            
            # Extract recipients
            to_header = next((h['value'] for h in headers if h['name'].lower() == 'to'), '')
            recipients = [r.strip() for r in to_header.split(',')] if to_header else []
            
            # Extract body
            body = self._extract_email_body(msg['payload'])
            
            # Parse timestamp
            internal_date = int(msg['internalDate']) / 1000  # Convert to seconds
            timestamp = datetime.fromtimestamp(internal_date)
            
            # Get labels
            labels = msg.get('labelIds', [])
            
            return {
                "user_id": user_id,
                "message_id": msg['id'],
                "thread_id": msg.get('threadId'),
                "subject": subject,
                "sender": sender,
                "recipients": recipients,
                "body": body,
                "timestamp": timestamp,
                "read": 'UNREAD' not in labels,
                "labels": labels
            }
        except Exception as e:
            print(f"Error parsing email message: {str(e)}")
            return None
    
    def _extract_email_body(self, payload: Dict) -> str:
        """Extract email body from Gmail API payload"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part.get('mimeType') == 'text/plain':
                    if 'data' in part['body']:
                        body_bytes = base64.urlsafe_b64decode(part['body']['data'])
                        body = body_bytes.decode('utf-8', errors='replace')
                        break
        elif 'body' in payload and 'data' in payload['body']:
            body_bytes = base64.urlsafe_b64decode(payload['body']['data'])
            body = body_bytes.decode('utf-8', errors='replace')
        
        return body
    
    async def send_email(self, user_id: str, to: List[str], subject: str, body: str, 
                        cc: List[str] = None, bcc: List[str] = None) -> Dict:
        """Send an email using Gmail API"""
        service = await self.get_gmail_service(user_id)
        
        if not service:
            return {"success": False, "error": "Gmail service not available"}
        
        try:
            # Create message
            message = MIMEMultipart()
            message['to'] = ', '.join(to)
            message['subject'] = subject
            
            if cc:
                message['cc'] = ', '.join(cc)
            if bcc:
                message['bcc'] = ', '.join(bcc)
            
            # Add body
            message.attach(MIMEText(body, 'plain'))
            
            # Encode message
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            create_message = {'raw': raw}
            
            # Send message
            sent = service.users().messages().send(
                userId="me", 
                body=create_message
            ).execute()
            
            return {
                "success": True, 
                "message_id": sent.get("id")
            }
            
        except HttpError as e:
            return {"success": False, "error": f"Gmail API error: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Error sending email: {str(e)}"}
    
    def get_email(self, user_id: str, email_id: str) -> Optional[Dict]:
        """Get a single email by ID"""
        try:
            email = self.email_collection.find_one({
                "_id": ObjectId(email_id), 
                "user_id": user_id
            })
            
            if not email:
                return None
            
            email["id"] = str(email.pop("_id"))
            return email
        except Exception as e:
            print(f"Error getting email: {str(e)}")
            return None
    
    def delete_email(self, user_id: str, email_id: str) -> bool:
        """Delete an email from database"""
        try:
            result = self.email_collection.delete_one({
                "_id": ObjectId(email_id), 
                "user_id": user_id
            })
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting email: {str(e)}")
            return False
    
    def update_email(self, user_id: str, email_id: str, updates: Dict) -> bool:
        """Update email properties"""
        try:
            result = self.email_collection.update_one(
                {"_id": ObjectId(email_id), "user_id": user_id},
                {"$set": updates}
            )
            return result.matched_count > 0
        except Exception as e:
            print(f"Error updating email: {str(e)}")
            return False
    
    def search_emails(self, user_id: str, filters: Dict) -> List[Dict]:
        """Search emails with various filters"""
        try:
            query = {"user_id": user_id}
            
            # Add filters
            if filters.get("read") is not None:
                query["read"] = filters["read"]
            
            if filters.get("sender"):
                query["sender"] = {"$regex": filters["sender"], "$options": "i"}
            
            if filters.get("subject"):
                query["subject"] = {"$regex": filters["subject"], "$options": "i"}
            
            if filters.get("query"):
                query["$or"] = [
                    {"subject": {"$regex": filters["query"], "$options": "i"}},
                    {"body": {"$regex": filters["query"], "$options": "i"}},
                    {"sender": {"$regex": filters["query"], "$options": "i"}}
                ]
            
            if filters.get("from_date") or filters.get("to_date"):
                date_filter = {}
                if filters.get("from_date"):
                    date_filter["$gte"] = filters["from_date"]
                if filters.get("to_date"):
                    date_filter["$lte"] = filters["to_date"]
                query["timestamp"] = date_filter
            
            if filters.get("labels"):
                query["labels"] = {"$in": filters["labels"]}
            
            # Execute query
            cursor = self.email_collection.find(query).sort("timestamp", -1)
            
            # Convert results
            emails = []
            for email in cursor:
                email["id"] = str(email.pop("_id"))
                emails.append(email)
            
            return emails
        except Exception as e:
            print(f"Error searching emails: {str(e)}")
            return []

# Global instance
email_service = EmailService()
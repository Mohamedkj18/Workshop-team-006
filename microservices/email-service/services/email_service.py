

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from bson.objectid import ObjectId
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Optional, Dict
from motor.motor_asyncio import AsyncIOMotorCollection
from db.mongodb import get_email_collection
from services.user_service_client import user_service_client
from config import settings
import asyncio

class EmailService:
    """Service for handling email operations"""
    
    def __init__(self):
        self.email_collection = get_email_collection()
    
    async def get_gmail_service(self, user_id: str):  # NOT async - just gets credentials
        """Get Gmail API service for the user"""
        # Get user's Google token from user service (synchronous call)
        user_data = await user_service_client.get_user_profile(user_id)
        print(f"[DEBUG] User data fetched for user_id {user_id}: {user_data}")
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
            loop = asyncio.get_running_loop()
            service = await loop.run_in_executor(None,lambda: build('gmail', 'v1', credentials=credentials))
            return service
            
        except Exception as e:
            print(f"Error creating Gmail service: {str(e)}")
            return None
    


    async def fetch_emails(self, user_id: str) -> Dict:
        service = await self.get_gmail_service(user_id)
        if not service:
            return {"success": False, "error": "Gmail service not available"}
        
        try:
            #This way, the blocking Gmail call runs in a separate thread, and your async app isn’t blocked.

            loop = asyncio.get_running_loop()
            
            # Gmail API call in executor (list messages)
            results = await loop.run_in_executor(
                None,
                lambda: service.users().messages().list(
                    userId='me', 
                    maxResults=settings.EMAIL_FETCH_BATCH_SIZE
                ).execute()
            )
            
            messages = results.get('messages', [])
            processed_count = 0
            
            for message in messages:
                # Async check in MongoDB
                existing = await self.email_collection.find_one({
                    "user_id": user_id,
                    "message_id": message['id']
                })
                if existing:
                    continue
                # Gmail API call in executor (get message)
                msg = await loop.run_in_executor(
                    None,
                    lambda: service.users().messages().get(
                        userId='me',
                        id=message['id'],
                        format='full'
                    ).execute()
                )
                
                email_data = self._parse_email_message(msg, user_id)
                if email_data:
                    await self.email_collection.insert_one(email_data)
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

    
    def _parse_email_message(self, msg: Dict, user_id: str) -> Optional[Dict]:  # Sync
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
            internal_date = int(msg['internalDate']) / 1000
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
    
    def _extract_email_body(self, payload: Dict) -> str:  # Sync
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
                        cc: List[str] = None, bcc: List[str] = None) -> Dict:  # ASYNC - Gmail API
        """Send an email using Gmail API"""
        service = await self.get_gmail_service(user_id)  # Sync call
        
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
            
            # Send message (Gmail API call)
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
    
    
    async def get_email(self, user_id: str, email_id: str) -> Optional[Dict]:  
        """Get a single email by ID"""
        try:
            email = await self.email_collection.find_one({
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
    


    async def search_emails(self, user_id: str, filters: Dict) -> List[Dict]:
        """Async search emails with filters"""
        try:
            query = {"user_id": user_id}

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

            cursor = self.email_collection.find(query).sort("timestamp", -1)
            results = await cursor.to_list(length=None)

            # Convert ObjectId to str
            for email in results:
                email["id"] = str(email.pop("_id"))

            return results

        except Exception as e:
            print(f"Error searching emails: {str(e)}")
            return []


    async def delete_email(self, user_id: str, email_id: str) -> bool:

        try:
            # 1. Find the email by ID (async)
            email_doc = await self.email_collection.find_one({
                "_id": ObjectId(email_id),
                "user_id": user_id
            })

            if not email_doc:
                return False

            gmail_message_id = email_doc.get("message_id")
            if not gmail_message_id:
                print("No Gmail message ID found, skipping Gmail deletion")
            else:
                try:
                    # 2. Get Gmail service for this user (async)
                    service = await self.get_gmail_service(user_id)
                    # 3. Delete message from Gmail (run in thread to avoid blocking)
                    await asyncio.to_thread(
                        lambda: service.users().messages().delete(
                            userId='me',
                            id=gmail_message_id
                        ).execute()
                    )
                    print(f"Gmail message {gmail_message_id} deleted")
                except HttpError as e:
                    print(f"Gmail API error: {e}")
                    return False

            # 4. Delete from your DB (async)
            result = await self.email_collection.delete_one({
                "_id": ObjectId(email_id),
                "user_id": user_id
            })

            return result.deleted_count > 0

        except Exception as e:
            print(f"Error deleting email: {str(e)}")
            return False

    # serves all update email purposes 
    async def update_email(self, user_id: str, email_id: str, updates: Dict) -> bool:
        """Update email properties in database"""
        try:
            # Add timestamp to updates
            updates_with_timestamp = {
                **updates,
                "updated_at": datetime.utcnow()
            }
            
            result = await self.email_collection.update_one(
                {"_id": ObjectId(email_id), "user_id": user_id},
                {"$set": updates_with_timestamp}
            )
            
            return result.matched_count > 0
        except Exception as e:
            print(f"Error updating email {email_id} for user {user_id}: {str(e)}")
            return False
        

    async def mark_email_read(self, user_id: str, email_id: str) -> Dict:
        """Mark email as read in database AND in Gmail"""
        try:
            # First, get the email from database to get the Gmail message_id
            email_doc = await self.email_collection.find_one({
                "_id": ObjectId(email_id),
                "user_id": user_id
            })
            
            if not email_doc:
                return {"success": False, "error": "Email not found"}
            
            gmail_message_id = email_doc.get("message_id")
            if not gmail_message_id:
                return {"success": False, "error": "Gmail message ID not found"}
            
            # Get Gmail service
            service = await self.get_gmail_service(user_id)
            if not service:
                return {"success": False, "error": "Gmail service not available"}
            
            # Mark as read in Gmail by removing the UNREAD label
            gmail_success = True
            loop = asyncio.get_running_loop()
            try:
                await loop.run_in_executor(
                    None,
                    lambda: service.users().messages().modify(
                        userId='me',
                        id=gmail_message_id,
                        body={'removeLabelIds': ['UNREAD']}
                    ).execute()
                )
                print(f"Successfully marked Gmail message {gmail_message_id} as read")
            except HttpError as gmail_error:
                print(f"Gmail API error marking as read: {str(gmail_error)}")
                gmail_success = False
            except Exception as gmail_error:
                print(f"Failed to mark Gmail message as read: {str(gmail_error)}")
                gmail_success = False
            
            # Update in database (always attempt this)
            result = await self.email_collection.update_one(
                {"_id": ObjectId(email_id), "user_id": user_id},
                {"$set": {
                    "read": True,
                    "updated_at": datetime.utcnow()
                }}
            )
            
            if result.matched_count > 0:
                print(f"Successfully marked email {email_id} as read in database")
                return {
                    "success": True,
                    "gmail_updated": gmail_success,
                    "database_updated": True,
                    "message": "Email marked as read"
                }
            else:
                return {"success": False, "error": "Failed to update database"}
                
        except Exception as e:
            print(f"Error marking email {email_id} as read for user {user_id}: {str(e)}")
            return {"success": False, "error": f"Unexpected error: {str(e)}"}



#might be redundant
    async def mark_email_unread(self, user_id: str, email_id: str) -> bool:
        """Mark email as unread in database AND in Gmail"""
        try:
            # Get the email from database to get the Gmail message_id
            email_doc = await self.email_collection.find_one({
                "_id": ObjectId(email_id), 
                "user_id": user_id
            })
            
            if not email_doc:
                print(f"Email {email_id} not found for user {user_id}")
                return False
            
            gmail_message_id = email_doc.get("message_id")
            if not gmail_message_id:
                print(f"No Gmail message_id found for email {email_id}")
                return False
            
            # Get Gmail service
            service = await self.get_gmail_service(user_id)
            if not service:
                print(f"Gmail service not available for user {user_id}")
                return False
            
            # Mark as unread in Gmail by adding the UNREAD label
            loop = asyncio.get_running_loop()
            try:
                await loop.run_in_executor(
                    None,
                    lambda: service.users().messages().modify(
                        userId='me',
                        id=gmail_message_id,
                        body={'addLabelIds': ['UNREAD']}
                    ).execute()
                )
                print(f"Successfully marked Gmail message {gmail_message_id} as unread")
            except Exception as gmail_error:
                print(f"Failed to mark Gmail message as unread: {str(gmail_error)}")
                # Continue to update database even if Gmail update fails
            
            # Update in database
            result = await self.email_collection.update_one(
                {"_id": ObjectId(email_id), "user_id": user_id},
                {"$set": {
                    "read": False,
                    "updated_at": datetime.utcnow()
                }}
            )
            
            if result.matched_count > 0:
                print(f"Successfully marked email {email_id} as unread in database")
                return True
            else:
                print(f"Failed to update email {email_id} in database")
                return False
                
        except Exception as e:
            print(f"Error marking email {email_id} as unread for user {user_id}: {str(e)}")
            return False
        

    async def move_to_trash(self, user_id: str, email_id: str) -> Dict:
        """Move email to trash in Gmail and update database"""
        try:
            # 1. Find the email in database to get Gmail message ID
            email_doc = await self.email_collection.find_one({
                "_id": ObjectId(email_id),
                    "user_id": user_id
            })
                
            if not email_doc:
                return {"success": False, "error": "Email not found"}
                
            gmail_message_id = email_doc.get("message_id")
            if not gmail_message_id:
                return {"success": False, "error": "Gmail message ID not found"}
                
            # 2. Get Gmail service
            service = await self.get_gmail_service(user_id)
            if not service:
                return {"success": False, "error": "Gmail service not available"}
                
            # 3. Move to trash in Gmail (using executor to avoid blocking)
            loop = asyncio.get_running_loop()
            try:
                await loop.run_in_executor(
                    None,
                    lambda: service.users().messages().trash(
                        userId='me',
                        id=gmail_message_id
                    ).execute()
                )
            except HttpError as e:
                return {"success": False, "error": f"Gmail API error: {str(e)}"}
                
                # 4. Update database to reflect trash status
            
            result = await self.email_collection.update_one(
                {"_id": ObjectId(email_id), "user_id": user_id},
                {"$set": {
                        "trashed": True,
                        "updated_at": datetime.utcnow()
                }}
                )
                    
            if result.matched_count == 0:
                    return {"success": False, "error": "Failed to update database"}
                    
            return {
                    "success": True,
                    "message": "Email moved to trash successfully"
                    }
                
        except Exception as e:
                print(f"Error moving email {email_id} to trash for user {user_id}: {str(e)}")
                return {"success": False, "error": f"Unexpected error: {str(e)}"}




    async def reply_to_email(self, user_id: str, email_id: str, 
                        reply_body: str, reply_to_all: bool = False,
                        additional_cc: List[str] = None, 
                        additional_bcc: List[str] = None) -> Dict:
        """Reply to an email using Gmail API"""
        try:
            # 1. Get the original email from database
            original_email = await self.email_collection.find_one({
                "_id": ObjectId(email_id),
                "user_id": user_id
            })
            
            if not original_email:
                return {"success": False, "error": "Original email not found"}
            
            # 2. Get Gmail service
            service = await self.get_gmail_service(user_id)
            if not service:
                return {"success": False, "error": "Gmail service not available"}
            
            # 3. Get the original Gmail message to extract reply info
            loop = asyncio.get_running_loop()
            try:
                original_msg = await loop.run_in_executor(
                    None,
                    lambda: service.users().messages().get(
                        userId='me',
                        id=original_email['message_id'],
                        format='full'
                    ).execute()
                )
            except HttpError as e:
                return {"success": False, "error": f"Could not fetch original message: {str(e)}"}
            
            # 4. Extract headers for reply
            headers = original_msg['payload']['headers']
            original_subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            original_sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
            original_to = next((h['value'] for h in headers if h['name'].lower() == 'to'), '')
            original_cc = next((h['value'] for h in headers if h['name'].lower() == 'cc'), '')
            message_id = next((h['value'] for h in headers if h['name'].lower() == 'message-id'), '')
            
            # 5. Build reply message
            reply_message = MIMEMultipart()
            
            # Set reply-to (original sender)
            reply_message['To'] = original_sender
            
            # Handle reply-to-all and additional recipients
            cc_recipients = []
            
            if reply_to_all:
                # Add original recipients to CC (excluding yourself)
                user_profile = await loop.run_in_executor(
                    None,
                    lambda: service.users().getProfile(userId='me').execute()
                )
                user_email = user_profile.get('emailAddress', '')
                
                all_recipients = []
                if original_to:
                    all_recipients.extend([email.strip() for email in original_to.split(',')])
                if original_cc:
                    all_recipients.extend([email.strip() for email in original_cc.split(',')])
                
                # Remove user's own email and original sender
                reply_all_cc = [email for email in all_recipients 
                            if email != user_email and email != original_sender]
                cc_recipients.extend(reply_all_cc)
            
            # Add additional CC recipients from request
            if additional_cc:
                cc_recipients.extend(additional_cc)
            
            # Remove duplicates and set CC if any recipients
            if cc_recipients:
                unique_cc = list(set(cc_recipients))  # Remove duplicates
                reply_message['Cc'] = ', '.join(unique_cc)
            
            # Add BCC recipients if provided
            if additional_bcc:
                reply_message['Bcc'] = ', '.join(additional_bcc)
            
            # Set subject (add "Re: " if not already there)
            if not original_subject.lower().startswith('re:'):
                reply_subject = f"Re: {original_subject}"
            else:
                reply_subject = original_subject
            reply_message['Subject'] = reply_subject
            
            # Set threading headers for proper conversation grouping
            if message_id:
                reply_message['In-Reply-To'] = message_id
                reply_message['References'] = message_id
            
            reply_message['Thread-Index'] = original_msg.get('threadId', '')
            
            # 6. Add reply body
            reply_message.attach(MIMEText(reply_body, 'plain'))
            
            # 7. Send the reply
            raw_message = base64.urlsafe_b64encode(reply_message.as_bytes()).decode()
            send_message = {
                'raw': raw_message,
                'threadId': original_msg.get('threadId')  # Keep in same conversation
            }
            
            try:
                sent_message = await loop.run_in_executor(
                    None,
                    lambda: service.users().messages().send(
                        userId='me',
                        body=send_message
                    ).execute()
                )
                
                return {
                    "success": True,
                    "message_id": sent_message.get("id"),
                    "thread_id": sent_message.get("threadId"),
                    "message": "Reply sent successfully"
                }
                
            except HttpError as e:
                return {"success": False, "error": f"Failed to send reply: {str(e)}"}
                
        except Exception as e:
            print(f"Error replying to email {email_id} for user {user_id}: {str(e)}")
            return {"success": False, "error": f"Unexpected error: {str(e)}"}



    async def forward_email(self, user_id: str, email_id: str, 
                        to: List[str], forward_message: str = "",
                        cc: List[str] = None, bcc: List[str] = None) -> Dict:
        """Forward an email to other recipients"""
        try:
            # 1. Get the original email from database
            original_email = await self.email_collection.find_one({
                "_id": ObjectId(email_id),
                "user_id": user_id
            })
            
            if not original_email:
                return {"success": False, "error": "Original email not found"}
            
            # 2. Get Gmail service
            service = await self.get_gmail_service(user_id)
            if not service:
                return {"success": False, "error": "Gmail service not available"}
            
            # 3. Get the original Gmail message to extract content
            loop = asyncio.get_running_loop()
            try:
                original_msg = await loop.run_in_executor(
                    None,
                    lambda: service.users().messages().get(
                        userId='me',
                        id=original_email['message_id'],
                        format='full'
                    ).execute()
                )
            except HttpError as e:
                return {"success": False, "error": f"Could not fetch original message: {str(e)}"}
            
            # 4. Extract original email details
            headers = original_msg['payload']['headers']
            original_subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            original_sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
            original_to = next((h['value'] for h in headers if h['name'].lower() == 'to'), '')
            original_date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
            
            # Extract original body
            original_body = self._extract_email_body(original_msg['payload'])
            
            # 5. Build forward message
            forward_msg = MIMEMultipart()
            
            # Set recipients
            forward_msg['To'] = ', '.join(to)
            
            if cc:
                forward_msg['Cc'] = ', '.join(cc)
            if bcc:
                forward_msg['Bcc'] = ', '.join(bcc)
            
            # Set subject with "Fwd: " prefix
            if not original_subject.lower().startswith('fwd:') and not original_subject.lower().startswith('fw:'):
                forward_subject = f"Fwd: {original_subject}"
            else:
                forward_subject = original_subject
            forward_msg['Subject'] = forward_subject
            
            # 6. Build forward body with original email content
            forward_body = ""
            
            # Add user's forward message if provided
            if forward_message.strip():
                forward_body += f"{forward_message}\n\n"
            
            # Add forwarded message header
            forward_body += "---------- Forwarded message ---------\n"
            forward_body += f"From: {original_sender}\n"
            if original_date:
                forward_body += f"Date: {original_date}\n"
            forward_body += f"Subject: {original_subject}\n"
            if original_to:
                forward_body += f"To: {original_to}\n"
            forward_body += "\n"
            
            # Add original message body
            forward_body += original_body
            
            # 7. Attach the complete forward body
            forward_msg.attach(MIMEText(forward_body, 'plain'))
            
            # 8. Send the forward
            raw_message = base64.urlsafe_b64encode(forward_msg.as_bytes()).decode()
            send_message = {'raw': raw_message}
            
            try:
                sent_message = await loop.run_in_executor(
                    None,
                    lambda: service.users().messages().send(
                        userId='me',
                        body=send_message
                    ).execute()
                )
                
                return {
                    "success": True,
                    "message_id": sent_message.get("id"),
                    "thread_id": sent_message.get("threadId"),
                    "message": "Email forwarded successfully"
                }
                
            except HttpError as e:
                return {"success": False, "error": f"Failed to forward email: {str(e)}"}
                
        except Exception as e:
            print(f"Error forwarding email {email_id} for user {user_id}: {str(e)}")
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
        
email_service = EmailService()
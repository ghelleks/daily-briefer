import os
import email
from datetime import datetime, timedelta
from typing import List, Optional, ClassVar, Dict, Any
import base64

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from ..models.briefing_models import ToolStatus
from ..constants import ACTION_LABELS


class GmailTodoProcessingToolInput(BaseModel):
    """Input schema for Gmail todo processing tool."""
    todoist_email: str = Field(description="Email address for Todoist inbox forwarding")
    days_back: int = Field(default=7, description="Number of days to look back for todo emails")
    max_emails: int = Field(default=20, description="Maximum number of todo emails to process")
    dry_run: bool = Field(default=False, description="Preview mode - analyze emails but don't forward/archive")
    quiet: bool = Field(default=False, description="Minimize output - only show summary")


class GmailTodoProcessingTool(BaseTool):
    """Tool for processing emails labeled 'todo' by forwarding to Todoist and archiving."""
    
    name: str = "gmail_todo_processing_tool"
    description: str = "Find emails labeled 'todo', forward them to a Todoist inbox email, and archive them"
    args_schema: type[BaseModel] = GmailTodoProcessingToolInput
    
    # Class-level constant to avoid Pydantic validation issues
    GMAIL_SCOPES: ClassVar[List[str]] = [
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/gmail.send'
    ]
    
    def __init__(self):
        super().__init__()
        self._service = None
        self._label_map = {}  # Maps label names to Gmail label IDs
        self._status = ToolStatus(
            tool_name="Gmail Todo Processing",
            available=False,
            last_check=datetime.now()
        )
    
    def _authenticate(self) -> bool:
        """Authenticate with Gmail API."""
        try:
            creds = None
            gmail_token_path = 'tokens/gmail_api_token.json'
            
            # Check for existing tokens
            if os.path.exists(gmail_token_path):
                try:
                    creds = Credentials.from_authorized_user_file(gmail_token_path, self.GMAIL_SCOPES)
                except Exception as scope_error:
                    # If there's a scope mismatch, we need to re-authenticate
                    if 'invalid_scope' in str(scope_error).lower():
                        if not getattr(self, '_quiet_mode', False):
                            print("⚠️  Scope mismatch detected. Todo processing requires Gmail send permissions.")
                            print("   Backing up existing token and re-authenticating...")
                        
                        # Backup the existing token
                        import shutil
                        backup_name = f"tokens/gmail_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        shutil.copy(gmail_token_path, backup_name)
                        os.remove(gmail_token_path)
                        if not getattr(self, '_quiet_mode', False):
                            print(f"   Existing token backed up to: {backup_name}")
                        
                        creds = None  # Force re-authentication
                    else:
                        raise scope_error
            
            # If there are no (valid) credentials available, let the user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                    except Exception as refresh_error:
                        if 'invalid_scope' in str(refresh_error).lower():
                            # Need to re-authenticate with new scopes
                            creds = None
                        else:
                            raise refresh_error
                
                if not creds:
                    if not getattr(self, '_quiet_mode', False):
                        print("🔐 Gmail todo processing requires authentication with send permissions...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'tokens/credentials.json', self.GMAIL_SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open(gmail_token_path, 'w') as token:
                    token.write(creds.to_json())
                if not getattr(self, '_quiet_mode', False):
                    print(f"   Gmail API token saved to: {gmail_token_path}")
            
            self._service = build('gmail', 'v1', credentials=creds)
            self._status.available = True
            self._status.error_message = None
            return True
            
        except Exception as e:
            self._status.available = False
            self._status.error_message = str(e)
            return False
    
    def _get_label_map(self) -> bool:
        """Build a map of label names to Gmail label IDs."""
        try:
            results = self._service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            # Build map of existing labels
            self._label_map = {label['name']: label['id'] for label in labels}
            return True
            
        except Exception as e:
            self._status.error_message = f"Failed to get label map: {str(e)}"
            return False
    
    def _get_todo_emails(self, days_back: int, max_emails: int) -> List[Dict[str, Any]]:
        """Get emails labeled with 'todo' from the specified time period."""
        try:
            # Build search query for todo emails
            date_filter = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
            search_query = f"label:todo after:{date_filter}"
            
            # Get message list
            results = self._service.users().messages().list(
                userId='me',
                q=search_query,
                maxResults=max_emails
            ).execute()
            
            messages = results.get('messages', [])
            todo_emails = []
            
            for msg in messages:
                try:
                    # Get full message details
                    message = self._service.users().messages().get(
                        userId='me',
                        id=msg['id']
                    ).execute()
                    
                    # Skip if in TRASH or already archived
                    labels = message.get('labelIds', [])
                    if 'TRASH' in labels:
                        continue
                    
                    todo_emails.append({
                        'id': msg['id'],
                        'message': message,
                        'labels': labels
                    })
                    
                except Exception as e:
                    if not getattr(self, '_quiet_mode', False):
                        print(f"Error getting message {msg['id']}: {e}")
                    continue
            
            return todo_emails
            
        except Exception as e:
            raise Exception(f"Failed to get todo emails: {str(e)}")
    
    def _extract_header_value(self, headers: List[dict], name: str) -> str:
        """Extract header value by name."""
        for header in headers:
            if header['name'].lower() == name.lower():
                return header['value']
        return ""
    
    def _decode_message_body(self, message) -> str:
        """Decode email message body."""
        try:
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body']['data']
                        return base64.urlsafe_b64decode(data).decode('utf-8')
                    elif part['mimeType'] == 'text/html':
                        data = part['body']['data'] 
                        return base64.urlsafe_b64decode(data).decode('utf-8')
            else:
                if message['payload']['mimeType'] in ['text/plain', 'text/html']:
                    data = message['payload']['body']['data']
                    return base64.urlsafe_b64decode(data).decode('utf-8')
            return ""
        except Exception:
            return ""
    
    def _create_forward_message(self, original_message: dict, todoist_email: str) -> str:
        """Create a forwarded email message with original subject preserved."""
        headers = original_message['payload'].get('headers', [])
        
        # Extract original email data
        original_sender = self._extract_header_value(headers, 'From')
        original_subject = self._extract_header_value(headers, 'Subject')
        original_date = self._extract_header_value(headers, 'Date')
        original_body = self._decode_message_body(original_message)
        
        # Create forwarded message
        msg = MIMEMultipart()
        msg['To'] = todoist_email
        msg['Subject'] = original_subject  # Preserve original subject for Todoist processing
        
        # Create forwarded email body
        forwarded_body = f"""---------- Forwarded message ----------
From: {original_sender}
Date: {original_date}
Subject: {original_subject}

{original_body}
"""
        
        # Add the body
        msg.attach(MIMEText(forwarded_body, 'plain'))
        
        # Return the raw message
        return {'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode()}
    
    def _forward_email(self, email_data: Dict[str, Any], todoist_email: str) -> bool:
        """Forward a single email to the Todoist inbox."""
        try:
            # Create the forwarded message
            forward_msg = self._create_forward_message(
                email_data['message'], 
                todoist_email
            )
            
            # Send the forwarded email
            self._service.users().messages().send(
                userId='me',
                body=forward_msg
            ).execute()
            
            return True
            
        except Exception as e:
            if not getattr(self, '_quiet_mode', False):
                print(f"Error forwarding email {email_data['id']}: {e}")
            return False
    
    def _archive_email(self, email_id: str) -> bool:
        """Archive an email by removing it from INBOX."""
        try:
            # Remove INBOX label to archive the email
            modify_request = {
                'removeLabelIds': ['INBOX']
            }
            
            self._service.users().messages().modify(
                userId='me',
                id=email_id,
                body=modify_request
            ).execute()
            
            return True
            
        except Exception as e:
            if not getattr(self, '_quiet_mode', False):
                print(f"Error archiving email {email_id}: {e}")
            return False
    
    def _run(self, todoist_email: str, days_back: int = 7, max_emails: int = 20, 
             dry_run: bool = False, quiet: bool = False) -> str:
        """
        Process todo emails by forwarding them to Todoist and archiving them.
        
        Args:
            todoist_email: Email address for Todoist inbox forwarding
            days_back: Number of days to look back for todo emails
            max_emails: Maximum number of todo emails to process
            dry_run: Preview mode - analyze emails but don't forward/archive
            quiet: Minimize output - only show summary
            
        Returns:
            String report containing processing results and status information
        """
        # Set quiet mode for suppressing verbose output
        self._quiet_mode = quiet
        
        if not self._authenticate():
            return f"GMAIL TODO PROCESSING FAILURE: Authentication failed. Error: {self._status.error_message}"
        
        if not self._get_label_map():
            return f"GMAIL TODO PROCESSING FAILURE: Label mapping failed. Error: {self._status.error_message}"
        
        try:
            # Get todo emails
            todo_emails = self._get_todo_emails(days_back, max_emails)
            
            processed_count = 0
            forwarded_count = 0
            archived_count = 0
            failed_count = 0
            
            report = f"GMAIL TODO PROCESSING REPORT\n"
            report += f"Processing Date: {datetime.now().isoformat()}\n"
            report += f"Todoist Email: {todoist_email}\n"
            report += f"Search Period: Last {days_back} days\n"
            report += f"Total Todo Emails Found: {len(todo_emails)}\n"
            report += f"DRY RUN MODE: {'Yes - No emails will be forwarded/archived' if dry_run else 'No - Emails will be processed'}\n\n"
            
            if not todo_emails:
                report += "No todo emails found in the specified time period.\n"
                return report
            
            if not quiet:
                report += "EMAIL PROCESSING RESULTS:\n"
            
            for email_data in todo_emails:
                try:
                    processed_count += 1
                    
                    headers = email_data['message']['payload'].get('headers', [])
                    subject = self._extract_header_value(headers, 'Subject')
                    sender = self._extract_header_value(headers, 'From')
                    
                    if dry_run:
                        # Dry run mode - just report what would be done
                        forwarded_count += 1
                        archived_count += 1
                        if not quiet:
                            report += f"  🔍 Email {processed_count}: From {sender[:30]}... Subject: {subject[:40]}... → Would forward and archive\n"
                    else:
                        # Actually process the email
                        forward_success = self._forward_email(email_data, todoist_email)
                        
                        if forward_success:
                            forwarded_count += 1
                            
                            # Archive the email after successful forwarding
                            archive_success = self._archive_email(email_data['id'])
                            
                            if archive_success:
                                archived_count += 1
                                if not quiet:
                                    report += f"  ✅ Email {processed_count}: {subject[:40]}... → Forwarded and archived\n"
                            else:
                                failed_count += 1
                                if not quiet:
                                    report += f"  ⚠️  Email {processed_count}: {subject[:40]}... → Forwarded but failed to archive\n"
                        else:
                            failed_count += 1
                            if not quiet:
                                report += f"  ❌ Email {processed_count}: {subject[:40]}... → Failed to forward\n"
                    
                except Exception as e:
                    failed_count += 1
                    if not quiet:
                        report += f"  ❌ Email {processed_count}: Error processing - {str(e)}\n"
                    continue
            
            report += f"\nSUMMARY:\n"
            report += f"  Processed: {processed_count} emails\n"
            
            if dry_run:
                report += f"  Would Forward: {forwarded_count} emails\n"
                report += f"  Would Archive: {archived_count} emails\n"
                report += f"\n💡 This was a DRY RUN - no actual emails were forwarded or archived.\n"
                report += f"   Remove --dry-run flag to process these emails.\n"
            else:
                report += f"  Successfully Forwarded: {forwarded_count} emails\n"
                report += f"  Successfully Archived: {archived_count} emails\n"
                report += f"  Failed: {failed_count} emails\n"
                
                if forwarded_count > 0:
                    report += f"\n✅ {forwarded_count} todo emails have been forwarded to {todoist_email}\n"
                if archived_count > 0:
                    report += f"📁 {archived_count} emails have been archived from your inbox\n"
            
            return report
            
        except Exception as e:
            self._status.available = False
            self._status.error_message = str(e)
            return f"GMAIL TODO PROCESSING FAILURE: {self._status.error_message}"
    
    def get_status(self) -> ToolStatus:
        """Get current tool status."""
        self._status.last_check = datetime.now()
        return self._status
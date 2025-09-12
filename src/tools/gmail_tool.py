import os
from datetime import datetime, timedelta
from typing import List, Optional, ClassVar
import base64
import email
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from ..models.briefing_models import EmailData, ToolStatus


class GmailToolInput(BaseModel):
    """Input schema for Gmail tool."""
    days_back: int = Field(default=7, description="Number of days to look back for emails")
    query: Optional[str] = Field(default=None, description="Gmail search query")
    max_results: int = Field(default=100, description="Maximum number of emails to retrieve")


class GmailTool(BaseTool):
    """Tool for interacting with Gmail API to retrieve and analyze emails."""
    
    name: str = "gmail_tool"
    description: str = "Retrieve emails from Gmail for the last N days and extract relevant information for daily briefing"
    args_schema: type[BaseModel] = GmailToolInput
    
    # Class-level constant to avoid Pydantic validation issues
    GMAIL_SCOPES: ClassVar[List[str]] = ['https://www.googleapis.com/auth/gmail.modify']
    
    def __init__(self):
        super().__init__()
        self._service = None
        self._status = ToolStatus(
            tool_name="Gmail",
            available=False,
            last_check=datetime.now()
        )
    
    def _authenticate(self) -> bool:
        """Authenticate with Gmail API."""
        try:
            creds = None
            gmail_token_path = 'tokens/gmail_api_token.json'
            
            # Token file stores the user's access and refresh tokens
            if os.path.exists(gmail_token_path):
                creds = Credentials.from_authorized_user_file(gmail_token_path, self.GMAIL_SCOPES)
            
            # If there are no (valid) credentials available, let the user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'tokens/credentials.json', self.GMAIL_SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open(gmail_token_path, 'w') as token:
                    token.write(creds.to_json())
            
            self._service = build('gmail', 'v1', credentials=creds)
            self._status.available = True
            self._status.error_message = None
            return True
            
        except Exception as e:
            self._status.available = False
            self._status.error_message = str(e)
            return False
    
    def _decode_message_body(self, message) -> str:
        """Decode email message body."""
        try:
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body']['data']
                        return base64.urlsafe_b64decode(data).decode('utf-8')
            else:
                if message['payload']['mimeType'] == 'text/plain':
                    data = message['payload']['body']['data']
                    return base64.urlsafe_b64decode(data).decode('utf-8')
            return ""
        except Exception:
            return ""
    
    def _extract_header_value(self, headers: List[dict], name: str) -> str:
        """Extract header value by name."""
        for header in headers:
            if header['name'].lower() == name.lower():
                return header['value']
        return ""
    
    def _run(self, days_back: int = 7, query: Optional[str] = None, max_results: int = 100) -> str:
        """
        Retrieve emails from Gmail.
        
        Args:
            days_back: Number of days to look back
            query: Gmail search query (optional)
            max_results: Maximum number of emails to retrieve
            
        Returns:
            String report containing email data and status information
        """
        if not self._authenticate():
            return f"GMAIL TOOL FAILURE: Authentication failed. Error: {self._status.error_message}"
        
        try:
            # Build search query
            date_filter = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
            search_query = f"after:{date_filter}"
            if query:
                search_query += f" {query}"
            
            # Get message list
            results = self._service.users().messages().list(
                userId='me',
                q=search_query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for msg in messages:
                try:
                    # Get full message
                    message = self._service.users().messages().get(
                        userId='me',
                        id=msg['id']
                    ).execute()
                    
                    headers = message['payload'].get('headers', [])
                    
                    # Extract email data
                    email_data = EmailData(
                        message_id=msg['id'],
                        sender=self._extract_header_value(headers, 'From'),
                        subject=self._extract_header_value(headers, 'Subject'),
                        body=self._decode_message_body(message),
                        timestamp=datetime.fromtimestamp(int(message['internalDate']) / 1000),
                        thread_id=message.get('threadId'),
                        labels=message.get('labelIds', [])
                    )
                    
                    emails.append(email_data)
                    
                except Exception as e:
                    print(f"Error processing message {msg['id']}: {e}")
                    continue
            
            # Generate report
            report = f"GMAIL DATA COLLECTION REPORT\n"
            report += f"Collection Date: {datetime.now().isoformat()}\n"
            report += f"Search Period: Last {days_back} days\n"
            report += f"Search Query: {search_query}\n"
            report += f"Total Emails Found: {len(emails)}\n\n"
            
            if emails:
                report += "EMAIL DATA:\n"
                for i, email in enumerate(emails, 1):
                    report += f"Email {i}:\n"
                    report += f"  ID: {email.message_id}\n"
                    report += f"  From: {email.sender}\n"
                    report += f"  Subject: {email.subject}\n"
                    report += f"  Timestamp: {email.timestamp.isoformat()}\n"
                    report += f"  Thread ID: {email.thread_id}\n"
                    report += f"  Labels: {', '.join(email.labels)}\n"
                    report += f"  Body (first 200 chars): {email.body[:200]}...\n\n"
            else:
                report += "No emails found in the specified time period.\n"
            
            report += f"TOOL STATUS: Gmail tool operational and authenticated successfully.\n"
            return report
            
        except HttpError as error:
            self._status.available = False
            self._status.error_message = f"Gmail API error: {error}"
            return f"GMAIL TOOL FAILURE: {self._status.error_message}"
        except Exception as e:
            self._status.available = False
            self._status.error_message = str(e)
            return f"GMAIL TOOL FAILURE: {self._status.error_message}"
    
    def get_status(self) -> ToolStatus:
        """Get current tool status."""
        self._status.last_check = datetime.now()
        return self._status
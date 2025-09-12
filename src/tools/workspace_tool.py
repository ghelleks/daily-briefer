import os
from datetime import datetime
from typing import List, Optional, Dict, Any, ClassVar

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from ..models.briefing_models import DocumentReference, ToolStatus


class WorkspaceToolInput(BaseModel):
    """Input schema for Workspace tool."""
    search_query: str = Field(description="Search query for documents")
    max_results: int = Field(default=20, description="Maximum number of documents to retrieve")


class WorkspaceTool(BaseTool):
    """Tool for interacting with Google Workspace APIs to search for documents."""
    
    name: str = "workspace_tool"
    description: str = "Search Google Drive and Workspace documents for context related to calendar events and emails"
    args_schema: type[BaseModel] = WorkspaceToolInput
    
    # Class-level constant to avoid Pydantic validation issues
    WORKSPACE_SCOPES: ClassVar[List[str]] = [
        'https://www.googleapis.com/auth/drive.readonly',
        'https://www.googleapis.com/auth/documents.readonly'
    ]
    
    def __init__(self):
        super().__init__()
        self._drive_service = None
        self._docs_service = None
        self._status = ToolStatus(
            tool_name="Google Workspace",
            available=False,
            last_check=datetime.now()
        )
    
    def _authenticate(self) -> bool:
        """Authenticate with Google Workspace APIs."""
        try:
            creds = None
            # Token file stores the user's access and refresh tokens
            if os.path.exists('tokens/token_workspace.json'):
                creds = Credentials.from_authorized_user_file('tokens/token_workspace.json', self.WORKSPACE_SCOPES)
            
            # If there are no (valid) credentials available, let the user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'tokens/credentials.json', self.WORKSPACE_SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open('tokens/token_workspace.json', 'w') as token:
                    token.write(creds.to_json())
            
            self._drive_service = build('drive', 'v3', credentials=creds)
            self._docs_service = build('docs', 'v1', credentials=creds)
            self._status.available = True
            self._status.error_message = None
            return True
            
        except Exception as e:
            self._status.available = False
            self._status.error_message = str(e)
            return False
    
    def _extract_doc_id_from_url(self, url: str) -> Optional[str]:
        """Extract document ID from Google Docs/Sheets/Slides URL."""
        import re
        
        # Google Docs URL pattern
        patterns = [
            r'docs\.google\.com/document/d/([a-zA-Z0-9-_]+)',
            r'docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)',
            r'docs\.google\.com/presentation/d/([a-zA-Z0-9-_]+)',
            r'drive\.google\.com/file/d/([a-zA-Z0-9-_]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _get_document_content(self, doc_id: str) -> Optional[str]:
        """Get text content from a Google Document."""
        try:
            document = self._docs_service.documents().get(documentId=doc_id).execute()
            content = document.get('body', {}).get('content', [])
            
            text_content = []
            for element in content:
                if 'paragraph' in element:
                    paragraph = element['paragraph']
                    for text_run in paragraph.get('elements', []):
                        if 'textRun' in text_run:
                            text_content.append(text_run['textRun']['content'])
            
            return ''.join(text_content)
        except Exception:
            return None
    
    def _search_drive(self, query: str, max_results: int) -> List[DocumentReference]:
        """Search Google Drive for documents."""
        try:
            # Search for files
            results = self._drive_service.files().list(
                q=f"fullText contains '{query}' and (mimeType='application/vnd.google-apps.document' or mimeType='application/vnd.google-apps.spreadsheet' or mimeType='application/vnd.google-apps.presentation')",
                pageSize=max_results,
                fields="files(id, name, mimeType, webViewLink, modifiedTime)"
            ).execute()
            
            files = results.get('files', [])
            documents = []
            
            for file in files:
                doc_type = {
                    'application/vnd.google-apps.document': 'google_doc',
                    'application/vnd.google-apps.spreadsheet': 'google_sheet',
                    'application/vnd.google-apps.presentation': 'google_slides'
                }.get(file['mimeType'], 'unknown')
                
                doc_ref = DocumentReference(
                    title=file['name'],
                    url=file['webViewLink'],
                    source='drive_search',
                    doc_type=doc_type
                )
                
                documents.append(doc_ref)
            
            return documents
            
        except Exception as e:
            print(f"Error searching Drive: {e}")
            return []
    
    def _run(self, search_query: str, max_results: int = 20) -> List[DocumentReference]:
        """
        Search Google Workspace for documents related to the query.
        
        Args:
            search_query: Query to search for in documents
            max_results: Maximum number of documents to return
            
        Returns:
            List of DocumentReference objects
        """
        if not self._authenticate():
            return []
        
        try:
            documents = self._search_drive(search_query, max_results)
            return documents
            
        except HttpError as error:
            self._status.available = False
            self._status.error_message = f"Workspace API error: {error}"
            return []
        except Exception as e:
            self._status.available = False
            self._status.error_message = str(e)
            return []
    
    def search_by_event_context(self, event_title: str, attendees: List[str]) -> List[DocumentReference]:
        """Search for documents related to a specific calendar event."""
        # Combine event title and attendee domains for search
        search_terms = [event_title]
        for attendee in attendees:
            if '@' in attendee:
                domain = attendee.split('@')[1]
                search_terms.append(domain)
        
        query = ' OR '.join(search_terms)
        return self._run(query, 10)
    
    def get_status(self) -> ToolStatus:
        """Get current tool status."""
        self._status.last_check = datetime.now()
        return self._status
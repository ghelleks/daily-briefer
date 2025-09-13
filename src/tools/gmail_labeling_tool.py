import os
from datetime import datetime, timedelta
from typing import List, Optional, ClassVar
import base64

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from ..models.briefing_models import ToolStatus
from ..constants import ACTION_LABELS, GMAIL_SYSTEM_LABELS


class GmailLabelingToolInput(BaseModel):
    """Input schema for Gmail labeling tool."""
    days_back: int = Field(default=7, description="Number of days to look back for emails")
    query: Optional[str] = Field(default=None, description="Gmail search query")
    max_results: int = Field(default=50, description="Maximum number of emails to process")
    skip_labeled: bool = Field(default=True, description="Skip emails that already have classification labels")
    dry_run: bool = Field(default=False, description="Preview mode - analyze emails but don't apply labels")
    quiet: bool = Field(default=False, description="Minimize output - only show summary")


class GmailLabelingTool(BaseTool):
    """Tool for labeling Gmail emails based on classification rules."""
    
    name: str = "gmail_labeling_tool"
    description: str = "Read unlabeled emails from Gmail, classify them, and apply appropriate labels"
    args_schema: type[BaseModel] = GmailLabelingToolInput
    
    # Class-level constant to avoid Pydantic validation issues
    GMAIL_SCOPES: ClassVar[List[str]] = [
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    
    # Use centralized label constants
    ACTION_LABELS: ClassVar[List[str]] = ACTION_LABELS
    GMAIL_SYSTEM_LABELS: ClassVar[List[str]] = GMAIL_SYSTEM_LABELS
    
    def __init__(self):
        super().__init__()
        self._service = None
        self._label_map = {}  # Maps label names to Gmail label IDs
        self._status = ToolStatus(
            tool_name="Gmail Labeling",
            available=False,
            last_check=datetime.now()
        )
    
    def _authenticate(self) -> bool:
        """Authenticate with Gmail API."""
        try:
            creds = None
            gmail_token_path = 'tokens/gmail_api_token.json'
            legacy_token_path = 'tokens/token.json'
            
            # Check for existing tokens (prefer descriptive name, but check legacy too)
            if os.path.exists(gmail_token_path):
                try:
                    creds = Credentials.from_authorized_user_file(gmail_token_path, self.GMAIL_SCOPES)
                except Exception as scope_error:
                    # If there's a scope mismatch, we need to re-authenticate
                    if 'invalid_scope' in str(scope_error).lower():
                        if not getattr(self, '_quiet_mode', False):
                            print("⚠️  Scope mismatch detected. Email labeling requires Gmail modify permissions.")
                            print("   Backing up existing token and re-authenticating...")
                        
                        # Backup the existing token
                        import shutil
                        backup_name = f"tokens/gmail_readonly_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        shutil.copy(gmail_token_path, backup_name)
                        os.remove(gmail_token_path)
                        if not getattr(self, '_quiet_mode', False):
                            print(f"   Existing token backed up to: {backup_name}")
                        
                        creds = None  # Force re-authentication
                    else:
                        raise scope_error
            elif os.path.exists(legacy_token_path):
                if not getattr(self, '_quiet_mode', False):
                    print("⚠️  Found legacy token.json file. Migrating to gmail_api_token.json...")
                try:
                    creds = Credentials.from_authorized_user_file(legacy_token_path, self.GMAIL_SCOPES)
                    # If successful, migrate to new name
                    import shutil
                    shutil.move(legacy_token_path, gmail_token_path)
                    if not getattr(self, '_quiet_mode', False):
                        print(f"   Token migrated from {legacy_token_path} to {gmail_token_path}")
                except Exception as scope_error:
                    if 'invalid_scope' in str(scope_error).lower():
                        if not getattr(self, '_quiet_mode', False):
                            print("   Legacy token has insufficient scope. Backing up and re-authenticating...")
                        backup_name = f"tokens/gmail_legacy_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        import shutil
                        shutil.copy(legacy_token_path, backup_name)
                        os.remove(legacy_token_path)
                        if not getattr(self, '_quiet_mode', False):
                            print(f"   Legacy token backed up to: {backup_name}")
                        creds = None
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
                        print("🔐 Gmail labeling requires authentication with modify permissions...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'tokens/credentials.json', self.GMAIL_SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run with descriptive name
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
            if 'invalid_scope' in str(e).lower():
                self._status.error_message = (
                    "Gmail API scope error. Email labeling requires modify permissions. "
                    "Please delete tokens/gmail_api_token.json and re-authenticate."
                )
            else:
                self._status.error_message = str(e)
            return False
    
    def _get_or_create_labels(self) -> bool:
        """Get or create the action classification labels in Gmail."""
        try:
            # Get existing labels
            results = self._service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            # Build map of existing labels
            existing_labels = {label['name']: label['id'] for label in labels}
            
            # Create missing action classification labels (not Gmail system labels)
            for label_name in self.ACTION_LABELS:
                if label_name in existing_labels:
                    self._label_map[label_name] = existing_labels[label_name]
                else:
                    # Create the action label
                    label_object = {
                        'name': label_name,
                        'labelListVisibility': 'labelShow',
                        'messageListVisibility': 'show'
                    }
                    
                    created_label = self._service.users().labels().create(
                        userId='me',
                        body=label_object
                    ).execute()
                    
                    self._label_map[label_name] = created_label['id']
            
            return True
            
        except Exception as e:
            self._status.error_message = f"Failed to create action labels: {str(e)}"
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
    
    def _has_action_label(self, email_labels: List[str]) -> bool:
        """Check if email already has an action classification label."""
        for label_id in email_labels:
            for label_name, mapped_id in self._label_map.items():
                if label_id == mapped_id:
                    return True
        return False
    
    def _should_skip_labeling(self, email_labels: List[str]) -> bool:
        """
        Check if email should be skipped from labeling.
        
        Skip emails that:
        - Are in spam/trash
        - Are drafts or sent emails
        - Already have our action classification labels
        """
        # Skip system folders that shouldn't be labeled
        skip_labels = ['SPAM', 'TRASH', 'DRAFT', 'SENT']
        for skip_label in skip_labels:
            if skip_label in email_labels:
                return True
        
        # Skip if already has our action classification labels
        return self._has_action_label(email_labels)
    
    def _apply_label(self, message_id: str, label_name: str) -> bool:
        """Apply an action classification label to an email."""
        try:
            if label_name not in self._label_map:
                return False
            
            # Remove any existing action labels first (but preserve Gmail system labels)
            remove_labels = []
            for existing_action_label in self.ACTION_LABELS:
                if existing_action_label != label_name and existing_action_label in self._label_map:
                    remove_labels.append(self._label_map[existing_action_label])
            
            # Apply the new action label and remove conflicting action labels only
            modify_request = {
                'addLabelIds': [self._label_map[label_name]],
                'removeLabelIds': remove_labels
            }
            
            self._service.users().messages().modify(
                userId='me',
                id=message_id,
                body=modify_request
            ).execute()
            
            return True
            
        except Exception as e:
            if not getattr(self, '_quiet_mode', False):
                print(f"Error applying action label {label_name} to message {message_id}: {e}")
            return False
    
    def _run(self, days_back: int = 7, query: Optional[str] = None, max_results: int = 50, skip_labeled: bool = True, dry_run: bool = False, quiet: bool = False) -> str:
        """
        Process and label emails from Gmail.
        
        Args:
            days_back: Number of days to look back
            query: Gmail search query (optional)
            max_results: Maximum number of emails to process
            skip_labeled: Skip emails that already have classification labels
            dry_run: Preview mode - analyze emails but don't apply labels
            quiet: Minimize output - only show summary
            
        Returns:
            String report containing labeling results and status information
        """
        # Set quiet mode for suppressing verbose output
        self._quiet_mode = quiet
        
        if not self._authenticate():
            return f"GMAIL LABELING TOOL FAILURE: Authentication failed. Error: {self._status.error_message}"
        
        # Only create labels if not in dry run mode
        if not dry_run and not self._get_or_create_labels():
            return f"GMAIL LABELING TOOL FAILURE: Label setup failed. Error: {self._status.error_message}"
        
        try:
            # Build search query for unlabeled emails in inbox only
            date_filter = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
            search_query = f"in:inbox after:{date_filter}"
            
            # Add action label exclusion if skipping labeled emails
            if skip_labeled:
                action_label_exclusions = " ".join([f"-label:{label}" for label in self.ACTION_LABELS])
                search_query += f" {action_label_exclusions}"
            
            if query:
                search_query += f" {query}"
            
            # Get message list
            results = self._service.users().messages().list(
                userId='me',
                q=search_query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            processed_count = 0
            labeled_count = 0
            skipped_count = 0
            
            report = f"GMAIL LABELING REPORT\n"
            report += f"Processing Date: {datetime.now().isoformat()}\n"
            report += f"Search Period: Last {days_back} days\n"
            report += f"Search Query: {search_query}\n"
            report += f"Total Emails Found: {len(messages)}\n"
            report += f"Skip Already Labeled: {skip_labeled}\n"
            report += f"DRY RUN MODE: {'Yes - No labels will be applied' if dry_run else 'No - Labels will be applied'}\n\n"
            
            if not messages:
                report += "No unlabeled emails found in the specified time period.\n"
                return report
            
            if not quiet:
                report += "EMAIL PROCESSING RESULTS:\n"
            
            for msg in messages:
                try:
                    processed_count += 1
                    
                    # Get full message
                    message = self._service.users().messages().get(
                        userId='me',
                        id=msg['id']
                    ).execute()
                    
                    headers = message['payload'].get('headers', [])
                    email_labels = message.get('labelIds', [])

                    # Double-check that email is in INBOX and not in TRASH
                    if 'TRASH' in email_labels or 'INBOX' not in email_labels:
                        skipped_count += 1
                        continue

                    # Skip if already labeled, in system folders, or should be skipped
                    if skip_labeled and self._should_skip_labeling(email_labels):
                        skipped_count += 1
                        continue
                    
                    # Extract email data for classification
                    sender = self._extract_header_value(headers, 'From')
                    subject = self._extract_header_value(headers, 'Subject')
                    body = self._decode_message_body(message)
                    
                    # Classify the email using Gmail categories and content analysis
                    classification = self._classify_email(sender, subject, body, email_labels)
                    
                    if classification:
                        if dry_run:
                            # Dry run mode - just report what would be done
                            labeled_count += 1
                            if not quiet:
                                report += f"  🔍 Email {processed_count}: {subject[:50]}... → Would label as '{classification}'\n"
                        else:
                            # Actually apply the label
                            if self._apply_label(msg['id'], classification):
                                labeled_count += 1
                                if not quiet:
                                    report += f"  ✅ Email {processed_count}: {subject[:50]}... → {classification}\n"
                            else:
                                if not quiet:
                                    report += f"  ❌ Email {processed_count}: {subject[:50]}... → Failed to apply label '{classification}'\n"
                    else:
                        if not quiet:
                            report += f"  ❓ Email {processed_count}: {subject[:50]}... → Could not classify\n"
                    
                except Exception as e:
                    if not quiet:
                        report += f"  ❌ Email {processed_count}: Error processing - {str(e)}\n"
                    continue
            
            report += f"\nSUMMARY:\n"
            report += f"  Processed: {processed_count} emails\n"
            if dry_run:
                report += f"  Would Label: {labeled_count} emails\n"
                report += f"  Skipped (already labeled): {skipped_count} emails\n"
                report += f"  Could Not Classify: {processed_count - labeled_count - skipped_count} emails\n"
                report += f"\n💡 This was a DRY RUN - no actual labels were applied to Gmail.\n"
                report += f"   Remove --dry-run flag to apply these labels.\n"
            else:
                report += f"  Successfully Labeled: {labeled_count} emails\n"
                report += f"  Skipped (already labeled): {skipped_count} emails\n"
                report += f"  Failed: {processed_count - labeled_count - skipped_count} emails\n"
            
            return report
            
        except HttpError as error:
            self._status.available = False
            self._status.error_message = f"Gmail API error: {error}"
            return f"GMAIL LABELING TOOL FAILURE: {self._status.error_message}"
        except Exception as e:
            self._status.available = False
            self._status.error_message = str(e)
            return f"GMAIL LABELING TOOL FAILURE: {self._status.error_message}"
    
    def _classify_email(self, sender: str, subject: str, body: str, labels: List[str]) -> Optional[str]:
        """
        Classify email based on required ACTION, not email type.
        
        Determines what action is needed with this email, using Gmail system labels
        as context but focusing on actionability.
        
        Args:
            sender: Email sender
            subject: Email subject
            body: Email body
            labels: Current Gmail labels (including system categories)
            
        Returns:
            Action classification label name or None if unable to classify
        """
        subject_lower = subject.lower()
        sender_lower = sender.lower()
        body_lower = body.lower()
        
        # Phase 1: Meeting-related actions (highest priority)
        meeting_keywords = ['meeting', 'invite', 'calendar', 'schedule', 'conference', 'zoom', 'teams', 'appointment']
        if any(word in subject_lower for word in meeting_keywords):
            return 'meetings'
        
        # Phase 2: Significant action required (todo)
        todo_keywords = ['payment', 'bill', 'invoice', 'action required', 'please complete', 'due date', 
                        'deadline', 'submit', 'approve', 'sign', 'register', 'application']
        todo_senders = ['school', 'physician', 'doctor', 'security', 'bank', 'finance', 'billing']
        
        # Check for failure/error notifications that require action
        failure_keywords = ['failed', 'declined', 'error', 'problem', 'issue', 'suspended', 'blocked']
        
        if (any(word in subject_lower for word in todo_keywords) or 
            any(sender in sender_lower for sender in todo_senders) or
            any(word in subject_lower for word in failure_keywords)):
            return 'todo'
        
        # Phase 3: Review/feedback requests
        review_keywords = ['review', 'feedback', 'opinion', 'thoughts', 'comment', 'please', 'input']
        google_docs_indicators = ['docs.google.com', 'has shared', 'commented on', 'shared with you']
        question_indicators = ['?', 'what do you think', 'can you', 'would you', 'could you']
        
        if (any(word in subject_lower for word in review_keywords) or
            any(indicator in body_lower for indicator in google_docs_indicators) or
            any(indicator in subject_lower for indicator in question_indicators)):
            return 'review'
        
        # Phase 4: Quick actions (2min)
        quick_keywords = ['confirm', 'verify', 'click here', 'one-click', 'quick', 'rsvp', 'yes/no']
        
        if any(word in subject_lower for word in quick_keywords):
            # Double-check it's not actually a complex action
            if any(word in subject_lower for word in ['payment', 'billing', 'account', 'financial']):
                return 'todo'  # Financial confirmations are not 2min tasks
            return '2min'
        
        # Phase 5: Default to fyi for informational content
        # Use Gmail system labels as context for default classification
        
        # CATEGORY_PROMOTIONS: Usually just informational
        if 'CATEGORY_PROMOTIONS' in labels:
            return 'fyi'
        
        # CATEGORY_FORUMS: Usually informational unless specific action needed
        if 'CATEGORY_FORUMS' in labels:
            return 'fyi'
        
        # CATEGORY_UPDATES: Usually informational but could be action if failure/error
        if 'CATEGORY_UPDATES' in labels:
            if any(word in subject_lower for word in failure_keywords):
                return 'todo'
            return 'fyi'
        
        # CATEGORY_SOCIAL: Usually just informational
        if 'CATEGORY_SOCIAL' in labels:
            return 'fyi'
        
        # CATEGORY_PRIMARY: Requires more analysis, but default to fyi if unclear
        # Most automated notifications end up here
        automated_senders = ['noreply', 'no-reply', 'donotreply', 'automated', 'system']
        if any(sender in sender_lower for sender in automated_senders):
            return 'fyi'
        
        # Default for everything else
        return 'fyi'
    
    def get_status(self) -> ToolStatus:
        """Get current tool status."""
        self._status.last_check = datetime.now()
        return self._status
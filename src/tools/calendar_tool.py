import os
from datetime import datetime, date, timedelta
from typing import List, Optional, ClassVar

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from ..models.briefing_models import CalendarEvent, ToolStatus


class CalendarToolInput(BaseModel):
    """Input schema for Calendar tool."""
    target_date: date = Field(description="Date to retrieve calendar events for")
    include_declined: bool = Field(default=False, description="Include declined events")


class CalendarTool(BaseTool):
    """Tool for interacting with Google Calendar API to retrieve events."""
    
    name: str = "calendar_tool"
    description: str = "Retrieve calendar events for a specific date to include in daily briefing"
    args_schema: type[BaseModel] = CalendarToolInput
    
    # Class-level constant to avoid Pydantic validation issues
    CALENDAR_SCOPES: ClassVar[List[str]] = ['https://www.googleapis.com/auth/calendar.readonly']
    
    def __init__(self):
        super().__init__()
        self._service = None
        self._status = ToolStatus(
            tool_name="Google Calendar",
            available=False,
            last_check=datetime.now()
        )
    
    def _authenticate(self) -> bool:
        """Authenticate with Google Calendar API."""
        try:
            creds = None
            # Token file stores the user's access and refresh tokens
            if os.path.exists('tokens/token_calendar.json'):
                creds = Credentials.from_authorized_user_file('tokens/token_calendar.json', self.CALENDAR_SCOPES)
            
            # If there are no (valid) credentials available, let the user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'tokens/credentials.json', self.CALENDAR_SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open('tokens/token_calendar.json', 'w') as token:
                    token.write(creds.to_json())
            
            self._service = build('calendar', 'v3', credentials=creds)
            self._status.available = True
            self._status.error_message = None
            return True
            
        except Exception as e:
            self._status.available = False
            self._status.error_message = str(e)
            return False
    
    def _parse_datetime(self, dt_data: dict) -> datetime:
        """Parse datetime from Google Calendar API response."""
        if 'dateTime' in dt_data:
            # Parse ISO format datetime
            dt_str = dt_data['dateTime']
            if dt_str.endswith('Z'):
                dt_str = dt_str[:-1] + '+00:00'
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        elif 'date' in dt_data:
            # All-day event
            return datetime.fromisoformat(dt_data['date'])
        else:
            raise ValueError("No valid datetime found in event")
    
    def _extract_meeting_url(self, event: dict) -> Optional[str]:
        """Extract virtual meeting URL from event."""
        # Check conferenceData
        if 'conferenceData' in event:
            entry_points = event['conferenceData'].get('entryPoints', [])
            for entry in entry_points:
                if entry.get('entryPointType') == 'video':
                    return entry.get('uri')
        
        # Check location for common meeting URLs
        location = event.get('location', '')
        if any(domain in location.lower() for domain in ['zoom.us', 'meet.google.com', 'teams.microsoft.com']):
            return location
        
        # Check description for meeting links
        description = event.get('description', '')
        import re
        url_pattern = r'https?://[^\s<>"\']*(?:zoom\.us|meet\.google\.com|teams\.microsoft\.com)[^\s<>"\']*'
        match = re.search(url_pattern, description)
        if match:
            return match.group()
        
        return None
    
    def _run(self, target_date: date, include_declined: bool = False) -> List[CalendarEvent]:
        """
        Retrieve calendar events for a specific date.
        
        Args:
            target_date: Date to retrieve events for
            include_declined: Whether to include declined events
            
        Returns:
            List of CalendarEvent objects
        """
        if not self._authenticate():
            return []
        
        try:
            # Set time bounds for the target date
            start_time = datetime.combine(target_date, datetime.min.time()).isoformat() + 'Z'
            end_time = datetime.combine(target_date + timedelta(days=1), datetime.min.time()).isoformat() + 'Z'
            
            # Get events from primary calendar
            events_result = self._service.events().list(
                calendarId='primary',
                timeMin=start_time,
                timeMax=end_time,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            calendar_events = []
            
            for event in events:
                try:
                    # Skip cancelled events
                    if event.get('status') == 'cancelled':
                        continue
                    
                    # Check attendance status
                    attendee_status = None
                    attendees = event.get('attendees', [])
                    for attendee in attendees:
                        if attendee.get('self'):
                            attendee_status = attendee.get('responseStatus')
                            break
                    
                    # Skip declined events unless explicitly requested
                    if not include_declined and attendee_status == 'declined':
                        continue
                    
                    # Extract attendee emails
                    attendee_emails = [a.get('email', '') for a in attendees if a.get('email')]
                    
                    # Parse start and end times
                    start_dt = self._parse_datetime(event['start'])
                    end_dt = self._parse_datetime(event['end'])
                    
                    # Create CalendarEvent object
                    calendar_event = CalendarEvent(
                        event_id=event['id'],
                        title=event.get('summary', 'No Title'),
                        start_time=start_dt,
                        end_time=end_dt,
                        location=event.get('location'),
                        virtual_meeting_url=self._extract_meeting_url(event),
                        description=event.get('description'),
                        attendees=attendee_emails,
                        organizer=event.get('organizer', {}).get('email'),
                        status=event.get('status', 'confirmed')
                    )
                    
                    calendar_events.append(calendar_event)
                    
                except Exception as e:
                    print(f"Error processing event {event.get('id', 'unknown')}: {e}")
                    continue
            
            return calendar_events
            
        except HttpError as error:
            self._status.available = False
            self._status.error_message = f"Calendar API error: {error}"
            return []
        except Exception as e:
            self._status.available = False
            self._status.error_message = str(e)
            return []
    
    def get_status(self) -> ToolStatus:
        """Get current tool status."""
        self._status.last_check = datetime.now()
        return self._status
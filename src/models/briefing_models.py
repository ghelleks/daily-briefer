from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class BriefingRequest(BaseModel):
    """Request model for generating a daily briefing."""
    target_date: date
    user_email: Optional[str] = None
    todoist_snapshot_path: str = "todoist-snapshot.md"


class EmailData(BaseModel):
    """Model for email data from Gmail."""
    message_id: str
    sender: str
    subject: str
    body: str
    timestamp: datetime
    thread_id: Optional[str] = None
    labels: List[str] = Field(default_factory=list)
    classification: Optional[str] = None  # fyi, review, quick, meetings
    attachments: List[Dict[str, Any]] = Field(default_factory=list)


class CalendarEvent(BaseModel):
    """Model for calendar event data."""
    event_id: str
    title: str
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    virtual_meeting_url: Optional[str] = None
    description: Optional[str] = None
    attendees: List[str] = Field(default_factory=list)
    organizer: Optional[str] = None
    status: str = "confirmed"  # confirmed, tentative, cancelled


class TodoistTask(BaseModel):
    """Model for Todoist task data."""
    task_id: Optional[str] = None
    title: str
    due_date: Optional[date] = None
    priority: int = 1
    project: Optional[str] = None
    completed: bool = False
    created_date: Optional[datetime] = None


class SuggestedTask(BaseModel):
    """Model for AI-suggested tasks."""
    title: str
    source: str  # email_id, event_id, etc.
    rationale: str
    estimated_duration: Optional[str] = None
    urgency: str = "normal"  # low, normal, high


class DocumentReference(BaseModel):
    """Model for document references found in emails/calendar."""
    title: str
    url: str
    source: str  # where it was found
    doc_type: Optional[str] = None  # google_doc, pdf, etc.


class ActionItem(BaseModel):
    """Model for action items in the briefing."""
    title: str
    source: str  # todoist, suggested
    due_date: Optional[date] = None
    estimated_duration: Optional[str] = None


class EmailSummarySection(BaseModel):
    """Model for email summary sections (FYI, Review, Quick)."""
    category: str  # fyi, review, quick
    items: List[Dict[str, Any]] = Field(default_factory=list)


class CalendarEventSummary(BaseModel):
    """Model for enriched calendar event summary."""
    event: CalendarEvent
    context: str
    related_documents: List[DocumentReference] = Field(default_factory=list)
    open_actions: List[str] = Field(default_factory=list)


class BriefingDocument(BaseModel):
    """Final briefing document model."""
    date: date
    generated_at: datetime
    action_items: List[ActionItem]
    email_summary: List[EmailSummarySection]
    daily_agenda: List[CalendarEventSummary]
    tool_failures: List[str] = Field(default_factory=list)
    
    
class ToolStatus(BaseModel):
    """Model for tracking tool availability and errors."""
    tool_name: str
    available: bool
    error_message: Optional[str] = None
    last_check: datetime
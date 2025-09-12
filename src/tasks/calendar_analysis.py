from crewai import Task
from datetime import date

from ..agents.calendar_analyst import create_calendar_analyst_agent


def create_calendar_analysis_task(target_date: date, verbose: bool = True) -> Task:
    """Create a task for analyzing calendar events and enriching them with context."""
    
    return Task(
        description=f"""Analyze calendar events for {target_date.isoformat()} and enrich them with comprehensive context.
        
        Your task is to process the calendar data collected by the Data Collector and:
        
        1. **Enrich Each Calendar Event** with context:
           - Search Gmail for relevant context, attachments, and recent discussions related to event titles and attendees
           - Search Google Workspace for related documents using event titles and attendee information
           - Identify meeting purposes from calendar descriptions and related communications
           - Extract virtual meeting URLs and ensure proper hyperlink formatting
        
        2. **Generate Comprehensive Event Summaries** with required formatting:
           - **Title, Time, and Location**: Start with event title in bold, followed by start/end times and location
           - **Virtual Meeting Links**: Hyperlink any virtual meeting URLs (Zoom, Google Meet, Teams)
           - **Attendees**: List who will be attending
           - **Context**: Describe meeting purpose based on calendar description and related emails/documents
           - **Related Documents**: Link directly to documents found in calendar invites or email threads
           - **Open Actions**: Extract action items from linked documents if present
        
        3. **Maintain Chronological Order**:
           - Ensure all events are ordered by start time
           - Handle all-day events appropriately
           - Group overlapping events logically
        
        4. **Context Search Strategy**:
           - Use event titles as primary search terms
           - Include attendee domain names in searches
           - Look for recent email threads mentioning the event
           - Search for shared documents related to meeting topics
        
        **Critical Requirements**:
        - Concern yourself only with items from a calendar. Ignore todo items.
        Maintain strict chronological ordering
        - Generate proper hyperlinks for all virtual meetings and documents
        - Provide comprehensive context without creating synthetic information
        - Handle tool failures gracefully and note them clearly
        - Focus on actionable information for meeting preparation
        
        **Expected Output**: Calendar analysis report containing:
        - Chronologically ordered calendar events
        - Enriched event summaries with full context
        - Related document links and references
        - Open action items from linked documents
        - Meeting preparation insights""",
        
        agent=create_calendar_analyst_agent(verbose=verbose),
        expected_output="Chronologically ordered calendar events with comprehensive context, related documents, and action items"
    )
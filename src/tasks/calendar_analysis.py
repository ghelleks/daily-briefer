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
        
        2. **Generate Intelligent Event Summaries** with smart formatting:
           - **Title and Essential Details**: Start with event title in bold, followed by only non-obvious details
           - **Smart Detail Inclusion**: Only include sub-bullets for details that add value:
             * Skip obvious details (birthdays are clearly all-day, lunch meetings are obviously about food)
             * Include times only when not standard or when duration matters
             * Include location only when it's not the default/obvious or when travel is involved
             * Include attendees only when it affects preparation or when the attendee list is significant
           - **Virtual Meeting Links**: Always hyperlink virtual meeting URLs (Zoom, Google Meet, Teams)
           - **Meaningful Context**: Only describe meeting purpose when there's actionable context beyond the title
           - **Related Documents**: Link directly to documents found in calendar invites or email threads
           - **Open Actions**: Extract action items from linked documents if present
           
        3. **Event Type Smart Formatting**:
           - **Personal Events** (birthdays, anniversaries): Simple title only unless additional context exists
           - **Routine Meetings** (1:1s, standups): Include context only if agenda/prep materials are available
           - **Complex Meetings** (reviews, planning): Always include attendees, context, and preparation materials
           - **All-day Events**: Skip time details, focus on any required actions or preparation
        
        4. **Maintain Chronological Order**:
           - Ensure all events are ordered by start time
           - Handle all-day events appropriately
           - Group overlapping events logically
        
        5. **Context Search Strategy**:
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
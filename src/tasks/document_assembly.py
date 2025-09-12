from crewai import Task
from datetime import date

from ..agents.document_synthesizer import create_document_synthesizer_agent


def create_document_assembly_task(target_date: date, verbose: bool = True) -> Task:
    """Create a task for assembling the final daily briefing document."""
    
    return Task(
        description=f"""Synthesize all analyzed data into a professional daily briefing document for {target_date.isoformat()}.
        
        Your task is to combine all previous analysis into a polished executive briefing:
        
        1. **Document Structure** - Create exactly three sections in this order:
           
           **Section 1: Action Items**
           - **From Todoist**: List existing tasks due on {target_date.isoformat()}
           - **Suggested**: List new task suggestions from email/calendar analysis
           - Use proper formatting and clear categorization
           
           **Section 2: Email Summary**
           - **Todo**: Emails requiring significant action (>2 minutes)
           - **2min**: Emails requiring quick action (<2 minutes)
           - **Review**: Emails requesting feedback or professional response
           - **Meetings**: Calendar invites and meeting-related communications
           - **FYI**: Informational items requiring no action
           - **CRITICAL**: Include hyperlinks for all document and website mentions
           
           **Section 3: Daily Agenda**
           - **Chronological order**: Events ordered by start time
           - **Rich context**: Include meeting purpose, attendees, and preparation needs
           - **Document links**: Direct links to relevant documents
           - **Open actions**: Action items from linked documents
           - **Virtual meeting links**: Properly hyperlinked meeting URLs
        
        2. **Quality Standards**:
           - Professional, concise, and direct tone
           - Executive-level summarization
           - Clear action orientation
           - Proper hyperlink formatting
           - No synthetic or placeholder data
        
        3. **Error Handling**:
           - Include notices for any tool failures at the beginning of relevant sections
           - Example: "Warning: The Google Calendar tool is currently unavailable..."
           - Be explicit about missing information
        
        4. **Final Verification Checklist**:
           - All three sections present and correctly ordered
           - Error handling notices added if tools failed
           - All possible hyperlinks included in Email Summary
           - Daily Agenda in strict chronological order
           - Professional formatting and tone maintained
        
        **Critical Requirements**:
        - Follow exact section structure and ordering
        - Include comprehensive hyperlinks
        - Maintain chronological calendar ordering
        - Provide clear tool failure notices
        - Use professional executive assistant tone
        - Generate actionable, specific content
        
        **Expected Output**: Complete daily briefing document ready for executive consumption with all required sections, proper formatting, and comprehensive hyperlinks""",
        
        agent=create_document_synthesizer_agent(verbose=verbose),
        expected_output="Professional daily briefing document with Action Items, Email Summary, and Daily Agenda sections"
    )
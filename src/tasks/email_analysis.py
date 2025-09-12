from crewai import Task
from datetime import date

from ..agents.email_analyst import create_email_analyst_agent


def create_email_analysis_task(target_date: date) -> Task:
    """Create a task for analyzing and categorizing emails."""
    
    return Task(
        description=f"""Analyze and categorize emails from the last 7 days for daily briefing on {target_date.isoformat()}.
        
        Your task is to process the email data collected by the Data Collector and:
        
        1. **Classify Emails** using the 7-label system:
           - **Todo**: Emails that require action and cannot be completed in less than 2 minutes
           - **2min**: Emails that require action and can be resolved in less than 2 minutes
           - **FYI**: Email reminders, automated updates about completed/ongoing events 
             (successful payments, transfers sent, deployments, shipments)
           - **Review**: Emails specifically asking for feedback, review, or opinion on documents in 
             professional/collaborative context, including Google Docs mentions and emails requiring 
             direct personal response (questions from individuals, personal conversations)
           - **Promotions**: Emails flagged as "Promotions" in Gmail
           - **Forums**: Emails from group lists and community discussions
           - * **news** - Emails from journalists or news organizations.
           - **Meetings**: Calendar invites, meeting changes, or meeting-related communications
        
        2. **Identify Suggested Tasks** from emails:
           - Direct questions (e.g., "Can you review the attached doc?")
           - Phrases indicating deliverables (e.g., "The report is due...")
           - Explicit action language (e.g., "Next steps are...")
           - Unresolved issues from email threads with high activity
        
        **Critical Requirements**:
        - Use proper email classification rules consistently
        - Extract actionable items for task suggestions
        - Provide structured classification data for use by subsequent briefing tasks
        - Never create synthetic data - only work with provided email data
        - Focus on accurate categorization, not presentation or summarization
        
        **Expected Output**: Email classification report containing:
        - Categorized email lists (Todo, 2min, FYI, Review, Promotions, Forums, Meetings) with email IDs and basic metadata
        - Suggested tasks derived from email analysis with source email references
        - Any classification challenges or ambiguous emails
        - Structured data ready for briefing presentation""",
        
        agent=create_email_analyst_agent(),
        expected_output="Structured email classification data with categorized lists, suggested tasks, and source references"
    )
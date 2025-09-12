from crewai import Task
from datetime import date

from ..agents.email_labeling_agent import create_email_labeling_agent


def create_email_labeling_task(days_back: int = 7, max_emails: int = 50) -> Task:
    """Create a task for labeling unlabeled emails in Gmail."""
    
    return Task(
        description=f"""Process and label unlabeled emails from Gmail for the last {days_back} days.

        Your task is to:

        1. **Retrieve Unlabeled Emails**: 
           - Access Gmail and retrieve emails from the last {days_back} days
           - Focus on emails that don't have classification labels (todo, 2min, fyi, review, news, promotions, forums, meetings)
           - Process up to {max_emails} emails in this batch

        2. **Classify Each Email** using the email classification knowledge:
           - **todo**: Emails requiring action that cannot be completed in less than 2 minutes
           - **2min**: Emails requiring action that can be resolved in less than 2 minutes  
           - **fyi**: Informational emails and automated updates
           - **review**: Emails asking for feedback, review, or opinion on documents
           - **news**: Emails from journalists or news organizations
           - **promotions**: Emails flagged as "Promotions" in Gmail
           - **forums**: Emails from group lists and community discussions
           - **meetings**: Meeting-related communications including invitations and notes

        3. **Apply Gmail Labels**:
           - Create classification labels in Gmail if they don't exist
           - Apply the appropriate label to each classified email
           - Remove conflicting classification labels if any exist
           - Ensure each email has exactly one classification label

        4. **Generate Processing Report**:
           - Summary of emails processed and labeled
           - Count of emails by classification type
           - Any errors or emails that couldn't be classified
           - Recommendations for improving classification accuracy

        **Critical Requirements**:
        - Use the email classification knowledge consistently for all decisions
        - If dry_run mode is enabled, analyze emails but DO NOT apply labels
        - Apply labels directly in Gmail only when not in dry run mode
        - Handle Gmail API authentication and rate limits gracefully
        - Process emails efficiently to avoid timeouts
        - Maintain accurate counts and provide detailed reporting

        **Expected Output**: Email labeling report containing:
        - Total emails processed and successfully labeled
        - Breakdown of emails by classification category
        - List of any emails that couldn't be classified with reasons
        - Overall success rate and any system issues encountered
        - Recommendations for future processing improvements""",
        
        agent=create_email_labeling_agent(),
        expected_output="Detailed email labeling report with processing statistics, classification breakdown, and any issues encountered"
    )
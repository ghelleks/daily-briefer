from crewai import Task
from datetime import date

from ..agents.email_labeling_agent import create_email_labeling_agent


def create_email_labeling_task(days_back: int = 7, max_emails: int = 50, verbose: bool = True) -> Task:
    """Create a task for labeling unlabeled emails in Gmail."""
    
    return Task(
        description=f"""Process and label unlabeled emails from Gmail for the last {days_back} days using the **Dual Email Classification System**.

        **CRITICAL: Use the Dual Classification System**
        
        This system uses TWO ORTHOGONAL classification approaches:
        1. **Email Type** (Gmail System Labels) - What the email IS (automatically handled by Gmail)
        2. **Action Classification** (Our Labels) - What to DO with it (your responsibility)

        Your task is to:

        1. **Retrieve Unlabeled Emails**: 
           - Access Gmail and retrieve emails from the last {days_back} days
           - Focus on emails that don't have ACTION classification labels (todo, 2min, fyi, review, meetings)
           - **RESPECT** existing Gmail system labels (CATEGORY_PROMOTIONS, CATEGORY_FORUMS, etc.)
           - Process up to {max_emails} emails in this batch

        2. **Apply ACTION Classification** using the email classification knowledge:
           - **todo**: Emails requiring action that cannot be completed in less than 2 minutes
           - **2min**: Emails requiring action that can be resolved in less than 2 minutes  
           - **fyi**: Informational emails and automated updates requiring no action
           - **review**: Emails asking for feedback, review, or opinion on documents
           - **meetings**: Meeting-related communications including invitations and notes
           
        **Email Type Context (Gmail System Labels - DO NOT DUPLICATE)**:
           - CATEGORY_PROMOTIONS (marketing emails) - use for context, don't create "promotions" label
           - CATEGORY_FORUMS (mailing lists) - use for context, don't create "forums" label
           - CATEGORY_UPDATES (notifications) - use for context, analyze for action needed
           - CATEGORY_SOCIAL (social media) - use for context, usually "fyi"
           - CATEGORY_PRIMARY (important emails) - use for context, analyze for action needed

        3. **Apply ACTION Labels Only**:
           - Create ACTION classification labels in Gmail if they don't exist (todo, 2min, fyi, review, meetings)
           - Apply exactly one ACTION label to each email
           - **PRESERVE** Gmail system labels - never remove or duplicate them
           - Remove conflicting ACTION labels only (not Gmail system labels)

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
        
        agent=create_email_labeling_agent(verbose=verbose),
        expected_output="Detailed email labeling report with processing statistics, classification breakdown, and any issues encountered"
    )
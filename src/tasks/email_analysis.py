from crewai import Task
from datetime import date

from ..agents.email_analyst import create_email_analyst_agent


def create_email_analysis_task(target_date: date, verbose: bool = True) -> Task:
    """Create a task for analyzing and categorizing emails."""
    
    return Task(
        description=f"""Analyze and categorize emails from the last 7 days for daily briefing on {target_date.isoformat()}.
        
        Your task is to process the email data collected by the Data Collector and apply the **Dual Email Classification System**.
        
        **CRITICAL: Use the Dual Classification System**
        
        This system uses TWO ORTHOGONAL classification approaches:
        1. **Email Type** (Gmail System Labels) - What the email IS (handled by Gmail automatically)
        2. **Action Classification** (Our Labels) - What to DO with it (your primary responsibility)
        
        **Your Primary Task: ACTION Classification**
        
        Classify each email by required ACTION using these 5 labels:
        
        - **todo**: Emails requiring action that cannot be completed in less than 2 minutes
          (payments, forms, significant decisions, complex responses)
        - **2min**: Emails requiring action that can be resolved in less than 2 minutes 
          (quick confirmations, simple replies, RSVP responses)
        - **review**: Emails requesting feedback, review, or opinion on documents/decisions
          (Google Docs sharing, feedback requests, review requests)
        - **meetings**: Meeting-related communications requiring calendar action
          (calendar invites, meeting changes, scheduling requests)
        - **fyi**: Informational emails requiring no action
          (notifications, updates, automated confirmations)
        
        **Email Type Context (Gmail System Labels)**
        
        Note and respect existing Gmail system labels as EMAIL TYPE context:
        - CATEGORY_PROMOTIONS (marketing emails)
        - CATEGORY_FORUMS (mailing lists, discussions) 
        - CATEGORY_UPDATES (notifications, confirmations)
        - CATEGORY_SOCIAL (social media notifications)
        - CATEGORY_PRIMARY (important emails)
        
        **Example of Dual Classification:**
        - A CATEGORY_UPDATES email about payment failure → ACTION: "todo"
        - A CATEGORY_FORUMS email asking for quick feedback → ACTION: "2min"
        - A CATEGORY_PROMOTIONS email with no action needed → ACTION: "fyi"
        
        **Additional Tasks:**
        
        2. **Identify Suggested Tasks** from emails:
           - Direct questions requiring action
           - Explicit deliverables and deadlines  
           - Unresolved issues needing follow-up
           - Action language indicators
        
        **Critical Requirements**:
        - Focus on ACTION classification, not email type
        - Respect Gmail system labels - don't duplicate them
        - Use email classification knowledge for consistent rules
        - Extract actionable items for task suggestions
        - Provide structured classification data
        - Never create synthetic data
        
        **Expected Output**: Email classification report containing:
        - ACTION-categorized email lists (todo, 2min, fyi, review, meetings) with email IDs and metadata
        - Email TYPE context from Gmail system labels
        - Suggested tasks derived from email analysis with source references
        - Any classification challenges or ambiguous emails
        - Structured data ready for briefing presentation""",
        
        agent=create_email_analyst_agent(verbose=verbose),
        expected_output="Structured email classification data with categorized lists, suggested tasks, and source references"
    )
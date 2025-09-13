import os
from crewai import Task
from datetime import date

from ..agents.todo_processing_agent import create_todo_processing_agent


def create_todo_processing_task(
    todoist_email: str = None,
    days_back: int = 7,
    max_emails: int = 20,
    dry_run: bool = False,
    verbose: bool = False
) -> Task:
    """
    Create a task for processing todo emails by forwarding them to Todoist and archiving them.
    
    Args:
        todoist_email: Email address for Todoist inbox forwarding
        days_back: Number of days to look back for todo emails
        max_emails: Maximum number of todo emails to process
        dry_run: Preview mode - analyze emails but don't forward/archive
        verbose: Whether to enable verbose output from CrewAI
        
    Returns:
        Task configured for todo email processing
    """
    
    # Get Todoist email from environment if not provided
    if not todoist_email:
        todoist_email = os.getenv('TODOIST_INBOX_EMAIL', '')
        if not todoist_email:
            todoist_email = 'TODOIST_EMAIL_NOT_CONFIGURED'
    
    
    return Task(
        description=f"""Process emails labeled 'todo' by forwarding them to a Todoist inbox and archiving them from Gmail.

        **CRITICAL: Todo Email Processing Workflow**
        
        This task implements a complete todo email processing pipeline that:
        1. Identifies emails with the 'todo' classification label
        2. Forwards them to an external Todoist inbox email
        3. Archives the original emails to maintain inbox organization
        
        **Your Responsibilities:**

        1. **Identify Todo Emails**:
           - Search Gmail for emails labeled with 'todo' from the last {days_back} days
           - Process up to {max_emails} emails in this batch
           - Skip emails that are already in TRASH or system folders
           - Focus on emails in the INBOX that require action

        2. **Forward to Todoist**:
           - Forward each todo email to: {todoist_email}
           - Preserve original subject line for optimal Todoist processing
           - Preserve original email content, sender, date, and subject information
           - Maintain proper email formatting for Todoist inbox processing
           - Handle forwarding errors gracefully with retry logic

        3. **Archive Original Emails**:
           - After successful forwarding, archive emails from Gmail INBOX
           - Remove INBOX label to move emails to All Mail (archived state)
           - Preserve the 'todo' label for future reference and reporting
           - Do not permanently delete emails - only archive them

        4. **Error Handling and Reporting**:
           - Track successful forwards, archives, and any failures
           - Provide detailed logging of each email processed
           - Generate comprehensive status report with counts and summaries
           - Handle Gmail API rate limits and network issues gracefully
           - Report any emails that couldn't be processed with reasons

        **Configuration for this run:**
        - Todoist Email: {todoist_email}
        - Days Back: {days_back}
        - Max Emails: {max_emails}
        - Dry Run Mode: {'ENABLED - No actual processing' if dry_run else 'DISABLED - Will process emails'}

        **Critical Requirements:**
        - Use the Gmail Todo Processing Tool for all email operations
        - Maintain email integrity during forwarding process
        - Ensure atomic operations (forward AND archive, or neither)
        - Respect Gmail API quotas and implement proper error handling
        - Generate detailed audit trail of all processed emails
        - If dry_run is enabled, simulate processing but make no actual changes

        **Expected Output**: Comprehensive todo processing report containing:
        - Total emails found and processed
        - Count of successfully forwarded emails
        - Count of successfully archived emails  
        - List of any processing failures with detailed error information
        - Summary statistics and recommendations for future processing
        - Verification that Todoist inbox has received the forwarded emails""",
        
        agent=create_todo_processing_agent(verbose=verbose),
        
        expected_output="""Detailed todo email processing report with:
1. Summary statistics (emails found, forwarded, archived, failed)
2. Processing status for each email (success/failure with reasons)
3. Verification of Todoist inbox delivery
4. Any errors encountered and recommended actions
5. Overall processing success rate and system health status""",
        
        # Task configuration
        context=[],  # No dependencies on other tasks for this standalone operation
        
        # Output configuration for integration
        output_file=None,  # Can be configured to save reports if needed
        
        # Additional task metadata
        max_execution_time=300  # 5 minutes timeout for processing
    )


def create_batch_todo_processing_task(
    todoist_email: str = None,
    max_batches: int = 3,
    emails_per_batch: int = 10,
    days_back: int = 7,
    dry_run: bool = False,
    verbose: bool = False
) -> Task:
    """
    Create a task for batch processing of todo emails with multiple iterations.
    
    This is useful for processing large volumes of todo emails while respecting
    Gmail API rate limits and ensuring reliable processing.
    
    Args:
        todoist_email: Email address for Todoist inbox forwarding
        max_batches: Maximum number of batches to process
        emails_per_batch: Number of emails to process per batch
        days_back: Number of days to look back for todo emails
        dry_run: Preview mode - analyze emails but don't forward/archive
        verbose: Whether to enable verbose output from CrewAI
        
    Returns:
        Task configured for batch todo email processing
    """
    
    # Get Todoist email from environment if not provided
    if not todoist_email:
        todoist_email = os.getenv('TODOIST_INBOX_EMAIL', '')
        if not todoist_email:
            todoist_email = 'TODOIST_EMAIL_NOT_CONFIGURED'
    
    return Task(
        description=f"""Process todo emails in multiple batches to handle large volumes while respecting API limits.

        **BATCH TODO EMAIL PROCESSING**
        
        Process todo emails in {max_batches} batches of {emails_per_batch} emails each:
        
        1. **Batch Processing Strategy**:
           - Run up to {max_batches} processing cycles
           - Process {emails_per_batch} emails per batch
           - Allow brief pauses between batches for API rate limiting
           - Continue until all todo emails are processed or max batches reached
        
        2. **Per-Batch Operations**:
           - Find emails labeled 'todo' from the last {days_back} days
           - Forward up to {emails_per_batch} emails to {todoist_email}
           - Archive successfully forwarded emails
           - Generate batch report before proceeding to next batch
        
        3. **Comprehensive Reporting**:
           - Track cumulative statistics across all batches
           - Report per-batch and overall success rates
           - Identify any emails requiring manual intervention
           - Provide recommendations for optimization
        
        **Configuration:**
        - Max Batches: {max_batches}
        - Emails per Batch: {emails_per_batch}
        - Todoist Email: {todoist_email}
        - Days Back: {days_back}
        - Dry Run: {'Yes' if dry_run else 'No'}""",
        
        agent=create_todo_processing_agent(verbose=verbose),
        
        expected_output="""Multi-batch todo processing report with:
1. Per-batch processing statistics
2. Cumulative totals across all batches
3. Overall success rate and processing efficiency
4. Any emails requiring manual attention
5. Recommendations for future batch processing""",
        
        max_execution_time=900  # 15 minutes for batch processing
    )
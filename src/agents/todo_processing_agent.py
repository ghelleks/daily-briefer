import os
from crewai import Agent
from typing import Optional

from ..tools.gmail_todo_processing_tool import GmailTodoProcessingTool


def create_todo_processing_agent(verbose: bool = True) -> Agent:
    """
    Create an agent specialized in processing todo emails by forwarding them to Todoist and archiving them.
    
    This agent uses the Gmail Todo Processing Tool to:
    1. Find emails labeled with 'todo'
    2. Forward them to a specified Todoist inbox email
    3. Archive the emails from the Gmail inbox
    4. Generate detailed processing reports
    
    Args:
        verbose: Whether to enable verbose output during processing
        
    Returns:
        Agent configured for todo email processing
    """
    
    # Initialize the Gmail todo processing tool
    gmail_todo_tool = GmailTodoProcessingTool()
    
    return Agent(
        role="Todo Email Processing Specialist",
        
        goal="""Process emails labeled 'todo' by forwarding them to a Todoist inbox email address 
        and then archiving them from Gmail to maintain inbox organization.""",
        
        backstory="""You are a specialized email automation agent responsible for streamlining 
        todo email workflows. Your expertise lies in efficiently identifying emails that have 
        been classified as requiring action (labeled 'todo'), forwarding them to external 
        task management systems like Todoist, and then organizing the Gmail inbox by archiving 
        processed emails.
        
        You understand the importance of:
        - Maintaining email context when forwarding to Todoist
        - Ensuring reliable delivery of forwarded emails
        - Providing clear audit trails of processed emails
        - Handling errors gracefully to prevent email loss
        - Respecting user preferences for batch processing limits
        
        Your work helps users maintain a clean, organized inbox while ensuring that important 
        action items are properly captured in their task management system.""",
        
        tools=[gmail_todo_tool],
        
        verbose=verbose,
        
        # Agent configuration for optimal performance
        max_iter=3,  # Limit iterations for focused task execution
        max_execution_time=300,  # 5 minutes timeout for processing
        
        # Memory and learning disabled for focused, stateless processing
        memory=False,
        
        # Custom instructions for consistent behavior
        allow_delegation=False,  # This agent works independently
        
        # Additional agent properties for enhanced functionality
        step_callback=None,  # Could be used for progress monitoring in future
    )


def create_todo_processing_agent_with_config(
    verbose: bool = True,
    todoist_email: Optional[str] = None,
    days_back: int = 7,
    max_emails: int = 20,
    dry_run: bool = False
) -> Agent:
    """
    Create a todo processing agent with pre-configured default parameters.
    
    This factory function creates an agent with specific configuration for common
    use cases, reducing the need to pass parameters repeatedly.
    
    Args:
        verbose: Whether to enable verbose output during processing
        todoist_email: Default Todoist inbox email (can be overridden in task)
        days_back: Default number of days to look back for todo emails
        max_emails: Default maximum number of emails to process
        dry_run: Default dry run mode setting
        
    Returns:
        Agent configured with default parameters
    """
    
    # Get Todoist email from environment if not provided
    if not todoist_email:
        todoist_email = os.getenv('TODOIST_INBOX_EMAIL', '')
    
    # Create the base agent
    agent = create_todo_processing_agent(verbose=verbose)
    
    # Store default configuration as agent attributes for reference
    agent._default_config = {
        'todoist_email': todoist_email,
        'days_back': days_back,
        'max_emails': max_emails,
        'dry_run': dry_run,
        'subject_prefix': os.getenv('TODO_FORWARD_SUBJECT_PREFIX', '[Todo] ')
    }
    
    return agent
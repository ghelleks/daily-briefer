import os
from datetime import datetime
from crewai import Crew, Process
from typing import Dict, Any, Optional

from ..tasks.todo_processing import create_todo_processing_task, create_batch_todo_processing_task


class TodoProcessingCrew:
    """Todo processing crew for automated forwarding of todo emails to Todoist and archiving."""
    
    def __init__(
        self, 
        todoist_email: str = None,
        days_back: int = 7, 
        max_emails: int = 20, 
        dry_run: bool = False,
        verbose: bool = False
    ):
        """
        Initialize the Todo Processing Crew.
        
        Args:
            todoist_email: Email address for Todoist inbox forwarding
            days_back: Number of days to look back for todo emails
            max_emails: Maximum number of emails to process in one run
            dry_run: Preview mode - analyze emails but don't forward/archive
            verbose: Whether to enable verbose output from CrewAI
        """
        self.todoist_email = todoist_email or os.getenv('TODOIST_INBOX_EMAIL', '')
        self.days_back = days_back
        self.max_emails = max_emails
        self.dry_run = dry_run
        self.verbose = verbose
        self.crew = None
        self._setup_crew()
    
    def _setup_crew(self):
        """Set up the crew with todo processing agent and task."""
        
        # Validate configuration
        if not self.todoist_email:
            raise ValueError(
                "Todoist email is required. Set TODOIST_INBOX_EMAIL environment variable "
                "or pass todoist_email parameter."
            )
        
        # Create todo processing task
        todo_processing_task = create_todo_processing_task(
            todoist_email=self.todoist_email,
            days_back=self.days_back, 
            max_emails=self.max_emails,
            dry_run=self.dry_run,
            verbose=self.verbose
        )
        
        # Create the crew with single agent and task
        self.crew = Crew(
            agents=[todo_processing_task.agent],
            tasks=[todo_processing_task],
            process=Process.sequential,
            verbose=self.verbose,
            output_log_file=False if not self.verbose else None,  # Disable log output in quiet mode
            memory=False  # Disable memory for focused, stateless processing
        )
    
    def kickoff(self, inputs: Dict[str, Any] = None) -> str:
        """
        Execute the todo email processing workflow.
        
        Args:
            inputs: Optional inputs for the crew
            
        Returns:
            The todo processing report
        """
        if inputs is None:
            inputs = {}
        
        # Add processing metadata to inputs
        inputs.update({
            'processing_time': datetime.now().isoformat(),
            'todoist_email': self.todoist_email,
            'days_back': self.days_back,
            'max_emails': self.max_emails,
            'dry_run': self.dry_run
        })
        
        try:
            result = self.crew.kickoff(inputs=inputs)
            return result
        except Exception as e:
            # Handle errors gracefully
            error_report = f"""# Todo Processing Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## ERROR: Todo Processing Failed

**Error Details**: {str(e)}

**Configuration**:
- Todoist Email: {self.todoist_email}
- Days back: {self.days_back}
- Max emails: {self.max_emails}
- Dry run: {self.dry_run}

**Troubleshooting Steps**:
1. Check Gmail API credentials and authentication
2. Verify proper Gmail API scopes (modify + send permissions)
3. Ensure Todoist inbox email is valid and accessible
4. Check network connectivity to Gmail API
5. Verify Gmail API rate limits have not been exceeded
6. Confirm todo emails exist in the specified time period

**Recommended Action**: Check the application logs for more detailed error information and verify Gmail API and Todoist email configuration.
"""
            return error_report
    
    def get_crew_info(self) -> Dict[str, Any]:
        """Get information about the crew configuration."""
        return {
            "todoist_email": self.todoist_email,
            "days_back": self.days_back,
            "max_emails": self.max_emails,
            "dry_run": self.dry_run,
            "num_agents": len(self.crew.agents) if self.crew else 0,
            "num_tasks": len(self.crew.tasks) if self.crew else 0,
            "process_type": "sequential",
            "memory_enabled": False,
            "agents": [agent.role for agent in self.crew.agents] if self.crew else [],
            "task_descriptions": [task.description[:100] + "..." for task in self.crew.tasks] if self.crew else []
        }


class BatchTodoProcessingCrew:
    """Todo processing crew for batch processing of large volumes of todo emails."""
    
    def __init__(
        self,
        todoist_email: str = None,
        max_batches: int = 3,
        emails_per_batch: int = 10,
        days_back: int = 7,
        dry_run: bool = False,
        verbose: bool = True
    ):
        """
        Initialize the Batch Todo Processing Crew.
        
        Args:
            todoist_email: Email address for Todoist inbox forwarding
            max_batches: Maximum number of batches to process
            emails_per_batch: Number of emails to process per batch
            days_back: Number of days to look back for todo emails
            dry_run: Preview mode - analyze emails but don't forward/archive
            verbose: Whether to enable verbose output from CrewAI
        """
        self.todoist_email = todoist_email or os.getenv('TODOIST_INBOX_EMAIL', '')
        self.max_batches = max_batches
        self.emails_per_batch = emails_per_batch
        self.days_back = days_back
        self.dry_run = dry_run
        self.verbose = verbose
        self.crew = None
        self._setup_crew()
    
    def _setup_crew(self):
        """Set up the crew with batch todo processing agent and task."""
        
        # Validate configuration
        if not self.todoist_email:
            raise ValueError(
                "Todoist email is required. Set TODOIST_INBOX_EMAIL environment variable "
                "or pass todoist_email parameter."
            )
        
        # Create batch todo processing task
        batch_todo_task = create_batch_todo_processing_task(
            todoist_email=self.todoist_email,
            max_batches=self.max_batches,
            emails_per_batch=self.emails_per_batch,
            days_back=self.days_back,
            dry_run=self.dry_run,
            verbose=self.verbose
        )
        
        # Create the crew
        self.crew = Crew(
            agents=[batch_todo_task.agent],
            tasks=[batch_todo_task],
            process=Process.sequential,
            verbose=self.verbose,
            output_log_file=False if not self.verbose else None,
            memory=False
        )
    
    def kickoff(self, inputs: Dict[str, Any] = None) -> str:
        """Execute the batch todo email processing workflow."""
        if inputs is None:
            inputs = {}
        
        # Add batch processing metadata
        inputs.update({
            'processing_time': datetime.now().isoformat(),
            'todoist_email': self.todoist_email,
            'max_batches': self.max_batches,
            'emails_per_batch': self.emails_per_batch,
            'days_back': self.days_back,
            'dry_run': self.dry_run
        })
        
        try:
            result = self.crew.kickoff(inputs=inputs)
            return result
        except Exception as e:
            return f"""# Batch Todo Processing Error - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ERROR: {str(e)}

Configuration: {self.max_batches} batches × {self.emails_per_batch} emails, 
Todoist: {self.todoist_email}, Dry run: {self.dry_run}

Please check logs and retry with smaller batch sizes if needed."""


def create_todo_processing_crew(
    todoist_email: str = None,
    days_back: int = 7, 
    max_emails: int = 20, 
    dry_run: bool = False,
    verbose: bool = False
) -> TodoProcessingCrew:
    """
    Factory function to create a Todo Processing Crew.
    
    Args:
        todoist_email: Email address for Todoist inbox forwarding
        days_back: Number of days to look back for todo emails
        max_emails: Maximum number of emails to process in one run
        dry_run: Preview mode - analyze emails but don't forward/archive
        verbose: Whether to enable verbose output from CrewAI
        
    Returns:
        Configured TodoProcessingCrew instance
    """
    return TodoProcessingCrew(
        todoist_email=todoist_email,
        days_back=days_back, 
        max_emails=max_emails, 
        dry_run=dry_run,
        verbose=verbose
    )


def create_batch_todo_processing_crew(
    todoist_email: str = None,
    max_batches: int = 3,
    emails_per_batch: int = 10,
    days_back: int = 7,
    dry_run: bool = False,
    verbose: bool = True
) -> BatchTodoProcessingCrew:
    """
    Factory function to create a Batch Todo Processing Crew.
    
    Args:
        todoist_email: Email address for Todoist inbox forwarding
        max_batches: Maximum number of batches to process
        emails_per_batch: Number of emails to process per batch
        days_back: Number of days to look back for todo emails
        dry_run: Preview mode - analyze emails but don't forward/archive
        verbose: Whether to enable verbose output from CrewAI
        
    Returns:
        Configured BatchTodoProcessingCrew instance
    """
    return BatchTodoProcessingCrew(
        todoist_email=todoist_email,
        max_batches=max_batches,
        emails_per_batch=emails_per_batch,
        days_back=days_back,
        dry_run=dry_run,
        verbose=verbose
    )
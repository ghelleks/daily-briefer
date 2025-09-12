from datetime import datetime
from crewai import Crew, Process
from typing import Dict, Any

from ..tasks.email_labeling import create_email_labeling_task
from ..knowledge import create_email_classification_knowledge


class EmailLabelingCrew:
    """Email labeling crew for automated Gmail email classification and labeling."""
    
    def __init__(self, days_back: int = 7, max_emails: int = 50):
        """
        Initialize the Email Labeling Crew.
        
        Args:
            days_back: Number of days to look back for emails
            max_emails: Maximum number of emails to process in one run
        """
        self.days_back = days_back
        self.max_emails = max_emails
        self.crew = None
        self._setup_crew()
    
    def _setup_crew(self):
        """Set up the crew with email labeling agent and task."""
        
        # Create email labeling task
        email_labeling_task = create_email_labeling_task(
            days_back=self.days_back, 
            max_emails=self.max_emails
        )
        
        # Create email classification knowledge source
        email_classification_knowledge = create_email_classification_knowledge()
        
        # Create the crew with single agent and task
        self.crew = Crew(
            agents=[email_labeling_task.agent],
            tasks=[email_labeling_task],
            knowledge_sources=[email_classification_knowledge],  # Use same knowledge as daily briefing
            process=Process.sequential,
            verbose=True,
            memory=False  # Disable memory for simpler processing
        )
    
    def kickoff(self, inputs: Dict[str, Any] = None) -> str:
        """
        Execute the email labeling process.
        
        Args:
            inputs: Optional inputs for the crew
            
        Returns:
            The email labeling report
        """
        if inputs is None:
            inputs = {}
        
        # Add processing metadata to inputs
        inputs['processing_time'] = datetime.now().isoformat()
        inputs['days_back'] = self.days_back
        inputs['max_emails'] = self.max_emails
        
        try:
            result = self.crew.kickoff(inputs=inputs)
            return result
        except Exception as e:
            # Handle errors gracefully
            error_report = f"""# Email Labeling Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## ERROR: Email Labeling Failed

**Error Details**: {str(e)}

**Configuration**:
- Days back: {self.days_back}
- Max emails: {self.max_emails}

**Troubleshooting Steps**:
1. Check Gmail API credentials and authentication
2. Verify proper Gmail API scopes (readonly + modify)
3. Ensure network connectivity to Gmail API
4. Check for Gmail API rate limits
5. Verify email classification knowledge is accessible

**Recommended Action**: Check the application logs for more detailed error information and verify Gmail API setup.
"""
            return error_report
    
    def get_crew_info(self) -> Dict[str, Any]:
        """Get information about the crew configuration."""
        return {
            "days_back": self.days_back,
            "max_emails": self.max_emails,
            "num_agents": len(self.crew.agents) if self.crew else 0,
            "num_tasks": len(self.crew.tasks) if self.crew else 0,
            "process_type": "sequential",
            "memory_enabled": False,
            "agents": [agent.role for agent in self.crew.agents] if self.crew else [],
            "task_descriptions": [task.description[:100] + "..." for task in self.crew.tasks] if self.crew else []
        }


def create_email_labeling_crew(days_back: int = 7, max_emails: int = 50) -> EmailLabelingCrew:
    """
    Factory function to create an Email Labeling Crew.
    
    Args:
        days_back: Number of days to look back for emails
        max_emails: Maximum number of emails to process in one run
        
    Returns:
        Configured EmailLabelingCrew instance
    """
    return EmailLabelingCrew(days_back=days_back, max_emails=max_emails)
import os
from datetime import date
from crewai import Crew, Process
from typing import Dict, Any

from .tasks.data_collection import create_data_collection_task
from .tasks.email_analysis import create_email_analysis_task
from .tasks.email_briefing import create_email_briefing_task
from .tasks.calendar_analysis import create_calendar_analysis_task
from .tasks.task_analysis import create_task_analysis_task
from .tasks.document_assembly import create_document_assembly_task
from .knowledge import create_email_classification_knowledge


class DailyBrieferCrew:
    """Main crew configuration for the Daily Briefer system."""
    
    def __init__(self, target_date: date):
        """
        Initialize the Daily Briefer Crew.
        
        Args:
            target_date: The date to generate the briefing for
        """
        self.target_date = target_date
        self.crew = None
        self._setup_crew()
    
    def _setup_crew(self):
        """Set up the crew with all agents and tasks."""
        
        # Create all tasks - we'll handle dependencies after creation
        data_collection_task = create_data_collection_task(self.target_date)
        email_analysis_task = create_email_analysis_task(self.target_date)
        email_briefing_task = create_email_briefing_task(self.target_date)
        calendar_analysis_task = create_calendar_analysis_task(self.target_date)
        task_analysis_task = create_task_analysis_task(self.target_date)
        document_assembly_task = create_document_assembly_task(self.target_date)
        
        # Set up task context dependencies with actual task objects
        email_analysis_task.context = [data_collection_task]
        email_briefing_task.context = [email_analysis_task]
        calendar_analysis_task.context = [data_collection_task]
        task_analysis_task.context = [data_collection_task]
        document_assembly_task.context = [email_briefing_task, calendar_analysis_task, task_analysis_task]
        
        # Create email classification knowledge source
        email_classification_knowledge = create_email_classification_knowledge()
        
        # Create the crew with sequential processing
        self.crew = Crew(
            agents=[
                data_collection_task.agent,
                email_analysis_task.agent,
                email_briefing_task.agent,
                calendar_analysis_task.agent,
                task_analysis_task.agent,
                document_assembly_task.agent
            ],
            tasks=[
                data_collection_task,
                email_analysis_task,
                email_briefing_task,
                calendar_analysis_task,
                task_analysis_task,
                document_assembly_task
            ],
            knowledge_sources=[email_classification_knowledge],  # Add email classification knowledge
            process=Process.sequential,  # Tasks run one after another
            verbose=True,
            memory=False  # Disable memory temporarily to avoid embedding issues
        )
    
    def kickoff(self, inputs: Dict[str, Any] = None) -> str:
        """
        Execute the daily briefing generation process.
        
        Args:
            inputs: Optional inputs for the crew (will include target_date)
            
        Returns:
            The generated daily briefing document
        """
        if inputs is None:
            inputs = {}
        
        # Add target date to inputs
        inputs['target_date'] = self.target_date.isoformat()
        inputs['target_date_formatted'] = self.target_date.strftime('%A, %B %d, %Y')
        inputs['day_name'] = self.target_date.strftime('%A').lower()
        inputs['wednesday'] = self.target_date.strftime('%A').lower()  # For template compatibility
        
        try:
            result = self.crew.kickoff(inputs=inputs)
            return result
        except Exception as e:
            # Handle errors gracefully
            error_briefing = f"""# Daily Briefing for {self.target_date.strftime('%A, %B %d, %Y')}

## ERROR: Briefing Generation Failed

**Error Details**: {str(e)}

**Troubleshooting Steps**:
1. Check your API credentials and authentication
2. Verify all required tools are accessible (Gmail, Calendar, Todoist MCP, Workspace)
3. Ensure proper network connectivity
4. Review the crew configuration and task dependencies

**Recommended Action**: Contact your system administrator or check the application logs for more detailed error information.
"""
            return error_briefing
    
    def get_crew_info(self) -> Dict[str, Any]:
        """Get information about the crew configuration."""
        return {
            "target_date": self.target_date.isoformat(),
            "num_agents": len(self.crew.agents) if self.crew else 0,
            "num_tasks": len(self.crew.tasks) if self.crew else 0,
            "process_type": "sequential",
            "memory_enabled": True,
            "agents": [agent.role for agent in self.crew.agents] if self.crew else [],
            "task_descriptions": [task.description[:100] + "..." for task in self.crew.tasks] if self.crew else []
        }


def create_daily_briefer_crew(target_date: date) -> DailyBrieferCrew:
    """
    Factory function to create a Daily Briefer Crew.
    
    Args:
        target_date: The date to generate the briefing for
        
    Returns:
        Configured DailyBrieferCrew instance
    """
    return DailyBrieferCrew(target_date)
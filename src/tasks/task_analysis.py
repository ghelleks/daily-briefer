from crewai import Task
from datetime import date

from ..agents.task_manager import create_task_manager_agent


def create_task_analysis_task(target_date: date) -> Task:
    """Create a task for processing Todoist tasks and generating task suggestions."""
    
    return Task(
        description=f"""Process Todoist tasks and generate intelligent task suggestions for {target_date.isoformat()}.
        
        Your task is to analyze task data and create comprehensive action items:
        
        1. **Process Todoist Tasks**:
           - Review tasks due on {target_date.isoformat()} from Todoist MCP server
           - Include overdue tasks that are still relevant
           - Format existing tasks for the Action Items section
           - Note any Todoist access issues or failures
        
        2. **Generate Suggested Tasks** from email and calendar analysis:
           - Analyze emails for action triggers:
             * Direct questions (e.g., "Can you review the attached doc?")
             * Phrases indicating deliverables (e.g., "The report is due...")
             * Explicit action language (e.g., "Next steps are...")
             * Unresolved issues from email threads with high activity
           - Analyze calendar events for preparation tasks:
             * Documents to review before meetings
             * Follow-up actions from previous meetings
             * Preparation tasks for upcoming presentations
        
        3. **Format Task Suggestions** using Todoist syntax:
           - Format: "Follow up with Jane about Project Mallory today [DAY_NAME] [15m]"
           - Include estimated durations when possible
           - Use natural language for due dates
           - DO NOT include project hashtags or labels
           - Prioritize by urgency and importance
        
        4. **Organize Action Items** into two subsections:
           - **From Todoist**: Existing tasks due on the target date
           - **Suggested**: New task suggestions derived from emails and calendar context
        
        **Critical Requirements**:
        - Use proper Todoist syntax for suggested tasks
        - Avoid duplicate tasks (don't suggest what's already in Todoist)
        - Focus on actionable, specific tasks
        - Include realistic time estimates
        - Prioritize urgent and important items
        - Do not create tasks for routine calendar attendance
        
        **Expected Output**: Task analysis report containing:
        - Formatted Todoist tasks due on target date
        - Intelligent task suggestions with proper syntax
        - Priority and urgency assessments
        - Time estimates for new tasks
        - Clear distinction between existing and suggested tasks""",
        
        agent=create_task_manager_agent(),
        expected_output="Comprehensive action items list with existing Todoist tasks and intelligent suggestions in proper format"
    )
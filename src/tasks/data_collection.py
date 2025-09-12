from crewai import Task
from datetime import date
from typing import Dict, Any

from ..agents.data_collector import create_data_collector_agent


def create_data_collection_task(target_date: date, verbose: bool = True) -> Task:
    """Create a task for collecting all data sources needed for the daily briefing."""
    
    return Task(
        description=f"""Collect comprehensive data for daily briefing on {target_date.isoformat()}.
        
        Your task is to gather data from all available sources:
        
        1. **Gmail Data**: Retrieve emails from the last 7 days using the Gmail tool
           - Get all emails with full content and metadata
           - Note any Gmail API failures or access issues
        
        2. **Calendar Data**: Retrieve calendar events for {target_date.isoformat()}
           - Get all accepted calendar events for the target date
           - Include event details, attendees, descriptions, and virtual meeting links
           - Note any Calendar API failures or access issues
        
        3. **Todoist Data**: Retrieve tasks due on {target_date.isoformat()}
           - Get tasks due on the target date via Todoist MCP server
           - Include overdue tasks that are still relevant
           - Note any Todoist MCP server failures or access issues
        
        4. **Workspace Context**: Prepare workspace search capability
           - Ensure Google Workspace tools are ready for document searches
           - Note any Workspace API failures or access issues
        
        **Critical Requirements**:
        - Document any tool failures clearly for error reporting
        - Return structured data that can be used by subsequent analysis tasks
        - Ensure data integrity and completeness
        - Do not create synthetic or placeholder data
        
        **Expected Output**: A comprehensive data collection report containing:
        - Raw email data (list of EmailData objects)
        - Calendar events (list of CalendarEvent objects) 
        - Todoist tasks (list of TodoistTask objects)
        - Tool status reports (list of ToolStatus objects)
        - Any error messages or warnings about failed data collection""",
        
        agent=create_data_collector_agent(verbose=verbose),
        expected_output="Structured data collection report with emails, calendar events, tasks, and tool status information"
    )
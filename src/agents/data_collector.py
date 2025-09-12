from crewai import Agent
from ..tools.gmail_tool import GmailTool
from ..tools.calendar_tool import CalendarTool
from ..tools.workspace_tool import WorkspaceTool
from ..tools.file_tool import FileTool
from ..tools.todoist_tool import TodoistTool


def create_data_collector_agent():
    """Create the Data Collector Agent responsible for gathering raw data from all sources."""
    
    # Combine all tools
    all_tools = [
        GmailTool(),
        CalendarTool(),
        WorkspaceTool(),
        FileTool(),
        TodoistTool()
    ]
    
    return Agent(
        role="Data Collector",
        goal="Gather comprehensive data from Gmail, Google Calendar, Google Workspace, Todoist, and local files to support daily briefing generation",
        backstory="""You are a meticulous data collection specialist with expertise in integrating 
        multiple data sources. Your role is to efficiently gather all necessary information from 
        Gmail (last 7 days), Google Calendar (target date), Google Workspace documents, and 
        Todoist. You ensure data integrity and handle any tool failures gracefully by 
        documenting what data could not be retrieved.
        
        For Todoist data, use the TodoistTool to retrieve tasks, projects, and other task 
        management information for the target date.""",
        tools=all_tools,
        llm="gemini/gemini-2.0-flash-lite",
        verbose=True,
        allow_delegation=False,
        max_iter=3
    )
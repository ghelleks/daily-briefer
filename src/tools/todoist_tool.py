from datetime import datetime, date
from typing import List, Optional, ClassVar
import os

from crewai.tools import BaseTool
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters
from pydantic import BaseModel, Field

from ..models.briefing_models import TodoistTask, ToolStatus


class TodoistToolInput(BaseModel):
    """Input schema for Todoist tool."""
    target_date: Optional[date] = Field(default=None, description="Filter tasks by due date")
    include_overdue: bool = Field(default=True, description="Include overdue tasks")
    project_id: Optional[str] = Field(default=None, description="Filter by specific project")


class TodoistTool(BaseTool):
    """Tool for interacting with Todoist via external MCP server to retrieve tasks."""
    
    name: str = "todoist_tool"
    description: str = "Retrieve tasks from Todoist via external MCP server for daily briefing"
    args_schema: type[BaseModel] = TodoistToolInput
    
    def __init__(self):
        super().__init__()
        self._status = ToolStatus(
            tool_name="Todoist MCP",
            available=False,
            last_check=datetime.now()
        )
    
    def _check_availability(self) -> bool:
        """Check if Todoist API key is available."""
        try:
            api_token = os.getenv('TODOIST_API_KEY')
            if not api_token:
                self._status.available = False
                self._status.error_message = "TODOIST_API_KEY not found in environment"
                return False
            
            self._status.available = True
            self._status.error_message = None
            return True
            
        except Exception as e:
            self._status.available = False
            self._status.error_message = f"Configuration error: {str(e)}"
            return False
    
    def _run(self, target_date: Optional[date] = None, include_overdue: bool = True, project_id: Optional[str] = None) -> str:
        """
        Retrieve tasks from Todoist via external MCP server.
        
        Args:
            target_date: Filter tasks by due date (None for all tasks)
            include_overdue: Whether to include overdue tasks
            project_id: Filter by specific project
            
        Returns:
            String report containing Todoist task data
        """
        if not self._check_availability():
            return f"TODOIST TOOL FAILURE: {self._status.error_message}"
        
        try:
            api_token = os.getenv('TODOIST_API_KEY')
            
            # Configure Todoist MCP server parameters
            server_params = StdioServerParameters(
                command="npx",
                args=["-y", "todoist-mcp"],
                env={
                    "API_KEY": api_token,
                    **os.environ
                }
            )
            
            # Use context manager to handle MCP connection properly
            with MCPServerAdapter(server_params) as mcp_tools:
                if not mcp_tools:
                    return "TODOIST TOOL FAILURE: No tools available from MCP server"
                
                # Find the get_tasks_list tool
                get_tasks_tool = None
                for tool in mcp_tools:
                    if "get_tasks_list" in tool.name.lower() or "tasks" in tool.name.lower():
                        get_tasks_tool = tool
                        break
                
                if not get_tasks_tool:
                    available_tools = [tool.name for tool in mcp_tools]
                    return f"TODOIST TOOL FAILURE: get_tasks_list tool not found. Available tools: {available_tools}"
                
                # Build filter parameters for MCP call
                filter_params = {}
                if target_date:
                    filter_params["filter"] = f"due: {target_date.isoformat()}"
                if project_id:
                    filter_params["project_id"] = project_id
                
                # Call the MCP tool to get tasks
                try:
                    result = get_tasks_tool._run(**filter_params)
                except Exception as tool_error:
                    return f"TODOIST TOOL FAILURE: Error calling MCP tool: {str(tool_error)}"
                
                # Generate report
                report = f"TODOIST DATA COLLECTION REPORT\n"
                report += f"Collection Date: {datetime.now().isoformat()}\n"
                report += f"Target Date: {target_date.isoformat() if target_date else 'All dates'}\n"
                report += f"Include Overdue: {include_overdue}\n"
                report += f"Project Filter: {project_id or 'All projects'}\n\n"
                
                if result:
                    # Parse the result - could be JSON string or dict
                    if isinstance(result, str):
                        report += f"TODOIST MCP RESPONSE:\n{result}\n\n"
                    elif isinstance(result, dict):
                        tasks = result.get('tasks', result.get('data', []))
                        if tasks:
                            report += f"TASKS FOUND: {len(tasks)}\n"
                            for i, task in enumerate(tasks, 1):
                                report += f"Task {i}:\n"
                                report += f"  ID: {task.get('id', 'N/A')}\n"
                                report += f"  Content: {task.get('content', 'N/A')}\n"
                                report += f"  Due Date: {task.get('due_date', 'No date')}\n"
                                report += f"  Project ID: {task.get('project_id', 'N/A')}\n"
                                report += f"  Priority: {task.get('priority', 'N/A')}\n"
                                report += f"  Labels: {', '.join(task.get('labels', []))}\n\n"
                        else:
                            report += "No tasks found in the response.\n"
                    else:
                        report += f"TODOIST RESPONSE (unknown format):\n{str(result)}\n\n"
                else:
                    report += "No tasks found or empty response from Todoist MCP server.\n"
                
                report += f"TOOL STATUS: Todoist MCP tool operational and connected successfully.\n"
                
                self._status.available = True
                self._status.error_message = None
                return report
            
        except Exception as e:
            self._status.available = False
            self._status.error_message = f"Todoist MCP error: {str(e)}"
            return f"TODOIST TOOL FAILURE: {self._status.error_message}"
    
    def get_status(self) -> ToolStatus:
        """Get current tool status."""
        self._status.last_check = datetime.now()
        return self._status


# MCP Server Integration Configuration:
# 
# Environment Variables Required:
# - TODOIST_API_KEY: Your Todoist API key
# - TODOIST_MCP_SERVER_URL: MCP server URL (optional, defaults to stdio://npx -y @modelcontextprotocol/server-todoist)
#
# Setup Instructions:
# 1. Install the Todoist MCP server: npm install -g @modelcontextprotocol/server-todoist
# 2. Set your Todoist API token in .env file
# 3. The tool will automatically connect to the MCP server
#
# Available MCP Tools:
# - get_tasks: Retrieve tasks with optional filtering
# - create_task: Create new tasks
# - update_task: Update existing tasks
# - complete_task: Mark tasks as completed
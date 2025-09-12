import os
from datetime import datetime, date, timedelta
from typing import List, Optional

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from ..models.briefing_models import ToolStatus


class FileToolInput(BaseModel):
    """Input schema for File tool."""
    file_path: str = Field(description="Path to the file to read")


class FileTool(BaseTool):
    """Tool for reading local files and documents."""
    
    name: str = "file_tool"
    description: str = "Read local files and documents for briefing context"
    args_schema: type[BaseModel] = FileToolInput
    
    def __init__(self):
        super().__init__()
        self._status = ToolStatus(
            tool_name="File System",
            available=True,
            last_check=datetime.now()
        )
    
    def _parse_markdown_content(self, content: str) -> str:
        """Parse markdown content and return cleaned text."""
        # Simple markdown parsing - could be enhanced with a proper markdown library
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove markdown headers
            line = line.strip()
            if line.startswith('#'):
                line = line.lstrip('#').strip()
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _run(self, file_path: str) -> str:
        """
        Read a file and return its contents.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            File content as string
        """
        try:
            if not os.path.exists(file_path):
                self._status.available = False
                self._status.error_message = f"File not found: {file_path}"
                return ""
            
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Parse markdown files for better readability
            if file_path.endswith('.md'):
                return self._parse_markdown_content(content)
            
            # Return raw content for other file types
            return content
            
        except Exception as e:
            self._status.available = False
            self._status.error_message = str(e)
            return ""
    
    def get_status(self) -> ToolStatus:
        """Get current tool status."""
        self._status.last_check = datetime.now()
        return self._status
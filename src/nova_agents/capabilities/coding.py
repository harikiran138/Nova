"""
Coding Capability - File operations, git, and code manipulation.

This capability groups file and code-related tools for software development tasks.
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
from src.nova_agents.capabilities.base import Capability
from src.nova_agents.tools.registry import ToolRegistry


class CodingCapability(Capability):
    """
    Capability for software development operations.
    
    Composes: file.read, file.write, file.list, shell.execute (for git)
    Note: File tools may need to be registered separately
    """
    
    def __init__(self, registry: ToolRegistry):
        super().__init__(registry)
        # These tools would need to be registered if they don't exist yet
        self._required_tools = []  # Flexible for now, as file tools may vary
    
    @property
    def name(self) -> str:
        return "coding"
    
    @property
    def description(self) -> str:
        return "Read, write, and manipulate code files, execute git operations"
    
    def execute(self, intent: str, **kwargs) -> Dict[str, Any]:
        """
        Execute coding operation based on intent.
        
        Args:
            intent: Coding goal (e.g., "read file", "create module")
            **kwargs: Operation-specific parameters:
                - file_path: Path to file
                - content: Content to write
                - operation: "read", "write", "list", "refactor"
        
        Returns:
            Dict with operation results
        """
        operation = kwargs.get("operation", "read")
        
        if operation == "read":
            return self.read_file(kwargs.get("file_path"))
        elif operation == "write":
            return self.write_file(kwargs.get("file_path"), kwargs.get("content", ""))
        elif operation == "list":
            return self.list_directory(kwargs.get("directory", "."))
        else:
            return {"success": False, "error": f"Unknown operation: {operation}"}
    
    def read_file(self, file_path: Optional[str]) -> Dict[str, Any]:
        """
        Read a file's contents.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dict with file contents or error
        """
        if not file_path:
            return {"success": False, "error": "file_path required"}
        
        try:
            path = Path(file_path)
            if not path.exists():
                return {"success": False, "error": f"File not found: {file_path}"}
            
            content = path.read_text()
            return {"success": True, "content": content, "path": str(path)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def write_file(self, file_path: Optional[str], content: str) -> Dict[str, Any]:
        """
        Write content to a file.
        
        Args:
            file_path: Path to the file
            content: Content to write
            
        Returns:
            Dict with success status
        """
        if not file_path:
            return {"success": False, "error": "file_path required"}
        
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            return {"success": True, "path": str(path), "bytes_written": len(content)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_directory(self, directory: str) -> Dict[str, Any]:
        """
        List files in a directory.
        
        Args:
            directory: Path to directory
            
        Returns:
            Dict with file list
        """
        try:
            path = Path(directory)
            if not path.exists() or not path.is_dir():
                return {"success": False, "error": f"Invalid directory: {directory}"}
            
            files = [str(f.relative_to(path)) for f in path.iterdir()]
            return {"success": True, "files": files, "directory": str(path)}
        except Exception as e:
            return {"success": False, "error": str(e)}

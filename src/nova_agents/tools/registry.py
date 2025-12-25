from typing import Dict, List, Optional
from src.nova_agents.tools.base import Tool

class ToolRegistry:
    """
    Central registry for managing available tools.
    Supports registration, retrieval, and listing of tools.
    """
    def __init__(self, workspace_dir: Optional[str] = None, **kwargs):
        self._tools: Dict[str, Tool] = {}
        self.workspace_dir = workspace_dir
        self.config = kwargs # Store other config for potential future use

    def register(self, tool: Tool):
        """
        Register a new tool instance.
        
        Args:
            tool (Tool): The tool instance to register.
        """
        if not isinstance(tool, Tool):
            raise TypeError(f"Object {tool} must be an instance of Tool")
        self._tools[tool.name] = tool

    @property
    def tools(self) -> Dict[str, Tool]:
        """Access internal tools dict."""
        return self._tools


    def get(self, name: str) -> Optional[Tool]:
        """
        Retrieve a tool by name.
        
        Args:
            name (str): The name of the tool.
            
        Returns:
            Optional[Tool]: The tool instance if found, else None.
        """
        return self._tools.get(name)

    def list(self) -> List[str]:
        """
        List all registered tool names.
        
        Returns:
            List[str]: A list of names of all registered tools.
        """
        return list(self._tools.keys())

    def list_descriptions(self) -> Dict[str, str]:
        """
        Get a mapping of tool names to their descriptions.
        """
        return {name: tool.description for name, tool in self._tools.items()}

from typing import Dict, List, Optional
from src.nova_agents.tools.base import Tool
# Import standard tools
from src.nova_agents.tools.vision_tools import VisionTool
from src.nova_agents.tools.browser_tools import BrowserTool
from src.nova_agents.tools.a2ui_tool import A2UITool

class ToolRegistry:
    """
    Central registry for managing available tools.
    Supports registration, retrieval, and listing of tools.
    """
    def __init__(self, workspace_dir: Optional[str] = None, **kwargs):
        self._tools: Dict[str, Tool] = {}
        self._ephemeral_tools: Dict[str, Tool] = {}
        self.workspace_dir = workspace_dir
        self.config = kwargs # Store other config for potential future use

        # Auto-register core capabilities if dependencies are met
        try:
            self.register(VisionTool())
        except Exception:
            pass # Vision dependencies missing
            
        try:
            self.register(BrowserTool())
        except Exception:
            pass # Browser dependencies missing (e.g. playwright)

        try:
            self.register(A2UITool())
        except Exception:
            pass

        try:
            from src.nova_agents.tools.posthog_tool import PostHogTool
            self.register(PostHogTool())
        except Exception:
            pass

        try:
            from src.nova_agents.tools.postman_tool import PostmanTool
            self.register(PostmanTool())
        except Exception:
            pass

    def register(self, tool: Tool):
        """
        Register a new tool instance.
        
        Args:
            tool (Tool): The tool instance to register.
        """
        if not isinstance(tool, Tool):
            raise TypeError(f"Object {tool} must be an instance of Tool")
        self._tools[tool.name] = tool

    def register_ephemeral_tool(self, tool: Tool):
        """Register a temporary tool for benchmarking."""
        if not isinstance(tool, Tool):
            raise TypeError(f"Object {tool} must be an instance of Tool")
        self._ephemeral_tools[tool.name] = tool

    def clear_ephemeral_tools(self):
        """Clear all temporary tools."""
        self._ephemeral_tools = {}

    @property
    def tools(self) -> Dict[str, Tool]:
        """Access internal tools dict (including ephemeral)."""
        combined = self._tools.copy()
        combined.update(self._ephemeral_tools)
        return combined

    def get(self, name: str) -> Optional[Tool]:
        """
        Retrieve a tool by name, checking ephemeral first.
        
        Args:
            name (str): The name of the tool.
            
        Returns:
            Optional[Tool]: The tool instance if found, else None.
        """
        if name in self._ephemeral_tools:
            return self._ephemeral_tools[name]
        return self._tools.get(name)

    def list(self) -> List[str]:
        """
        List all registered tool names.
        
        Returns:
            List[str]: A list of names of all registered tools.
        """
        return list(self.tools.keys())

    def list_descriptions(self) -> Dict[str, str]:
        """
        Get a mapping of tool names to their descriptions.
        """
        return {name: tool.description for name, tool in self._tools.items()}

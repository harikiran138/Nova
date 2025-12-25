import os
import sys
import importlib.util
import inspect
from typing import Dict, List, Any
from .base import BaseTool

class ToolRegistry:
    """
    Registry for managing and discovering ADK tools.
    """
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register_tool(self, tool: BaseTool) -> None:
        """
        Register a tool instance.
        
        Args:
            tool: The initialized tool instance.
        """
        if not isinstance(tool, BaseTool):
            raise TypeError("Tool must be an instance of BaseTool")
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> BaseTool:
        """Get a tool by name."""
        return self._tools.get(name)

    def get_tools(self) -> Dict[str, BaseTool]:
        """Get all registered tools."""
        return self._tools

    def discover_tools(self, directory: str) -> None:
        """
        Discover and register tools from a directory.
        
        Args:
            directory: Path to the directory to scan for tools.
        """
        if not os.path.exists(directory):
            return

        for filename in os.listdir(directory):
            if filename.endswith(".py") and not filename.startswith("__"):
                file_path = os.path.join(directory, filename)
                module_name = filename[:-3]
                
                # Import module dynamically
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)
                    
                    # Inspect module for BaseTool subclasses
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, BaseTool) and 
                            obj is not BaseTool):
                            try:
                                # Instantiate the tool
                                # Note: This assumes tools have a no-arg constructor or we can handle it
                                # For ADK compliance, we might enforce __init__ pattern, 
                                # but for now we instantiate assuming defaults are handled or no-args.
                                # The BaseTool __init__ takes name and description, so subclasses 
                                # MUST call super() with those or have hardcoded ones.
                                # Let's assume the subclass __init__ handles providing them to super.
                                tool_instance = obj()
                                self.register_tool(tool_instance)
                            except Exception as e:
                                print(f"Failed to load tool {name} from {filename}: {e}")

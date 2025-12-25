import importlib
import inspect
import os
import sys
from typing import Dict, Type, List, Optional
from .base import BaseTool

class ToolRegistry:
    """Minimal ADK Tool Registry used in tests."""
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register_tool(self, tool: BaseTool):
        if not isinstance(tool, BaseTool):
            raise TypeError("tool must be instance of BaseTool")
        self._tools[tool.name] = tool

    def get_tools(self) -> List[str]:
        return list(self._tools.keys())

    def get_tool(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def discover_tools(self, directory: str):
        """Discover and register tools from python files in a directory.
        A tool is any subclass of BaseTool with a no-arg constructor.
        """
        for fname in os.listdir(directory):
            if not fname.endswith(".py") or fname.startswith("_"):
                continue
            mod_name = os.path.splitext(fname)[0]
            try:
                module = importlib.import_module(mod_name)
            except Exception:
                # Try file-based import to avoid sys.path issues
                try:
                    spec = importlib.util.spec_from_file_location(mod_name, os.path.join(directory, fname))
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)  # type: ignore
                    else:
                        continue
                except Exception:
                    continue
            # Find subclasses
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseTool) and obj is not BaseTool:
                    try:
                        instance = obj()
                        self.register_tool(instance)
                    except Exception:
                        pass

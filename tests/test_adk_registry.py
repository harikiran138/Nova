import os
import sys
import pytest
from src.agent_core.adk.base import BaseTool
from src.agent_core.adk.registry import ToolRegistry

# Helper to create a dummy tool file
def create_dummy_tool(path, tool_name="MyTestTool"):
    content = f"""
from src.agent_core.adk.base import BaseTool

class {tool_name}(BaseTool):
    def __init__(self):
        super().__init__(name="{tool_name}", description="Description for {tool_name}")

    def execute(self, **kwargs):
        return "Executed"
"""
    with open(path, "w") as f:
        f.write(content)

def test_registry_registration():
    """Test manual registration of tools."""
    registry = ToolRegistry()
    
    class ManualTool(BaseTool):
        def execute(self, **kwargs):
            return "Manual"
            
    tool = ManualTool(name="manual", description="manual")
    registry.register_tool(tool)
    
    assert "manual" in registry.get_tools()
    assert registry.get_tool("manual") == tool

def test_registry_discovery(tmp_path):
    """Test discovery of tools from a directory."""
    # Create a dummy tool in a temporary directory
    tool_file = tmp_path / "custom_tool.py"
    create_dummy_tool(tool_file, "AutoTool")
    
    registry = ToolRegistry()
    
    # Add tmp_path to sys.path so import_module works (simplified discovery)
    # In a real scenario, discovery might use importlib.util.spec_from_file_location
    sys.path.append(str(tmp_path))
    
    try:
        registry.discover_tools(str(tmp_path))
        
        # Check if tool was discovered and registered
        # The tool name in the class is "AutoTool"
        assert "AutoTool" in registry.get_tools()
        discovered_tool = registry.get_tool("AutoTool")
        assert isinstance(discovered_tool, BaseTool)
        assert discovered_tool.name == "AutoTool"
    finally:
        sys.path.remove(str(tmp_path))

from typing import Dict, Any, Optional
from src.nova_agents.tools.registry import ToolRegistry
from src.nova_agents.core.policies import SafetyPolicy

class ToolExecutor:
    """
    Centralized executor for tool execution.
    Handles tool lookup, policy checks, and execution.
    """
    def __init__(self, registry: ToolRegistry, policies: SafetyPolicy):
        self.registry = registry
        self.policies = policies

    def execute(self, tool_name: str, **params) -> Any:
        """
        Execute a tool by name with the given parameters.
        
        Args:
            tool_name (str): The name of the tool to execute.
            **params: Arguments for the tool.
            
        Returns:
            Any: The result of the tool execution, or a blocked status.
        """
        tool = self.registry.get(tool_name)
        
        if not tool:
            return {"status": "ERROR", "message": f"Tool '{tool_name}' not found."}

        if not self.policies.check(tool, **params):
            return {"status": "BLOCKED", "message": f"Tool '{tool_name}' blocked by safety policy."}

        try:
            return tool.execute(**params)
        except Exception as e:
            return {"status": "ERROR", "message": f"Tool execution failed: {str(e)}"}

from typing import Dict, Any
from src.nova_agents.tools.base import Tool
from src.nova_ops.safety import SafetyPolicy
from src.nova_agents.core.policy_engine import PolicyEngine, RiskPolicy, RateLimitPolicy, PermissionPolicy

class SafetyPolicy:
    """
    Policy engine to enforce safety constraints on tool execution.
    """
    def check(self, tool: Tool, **kwargs) -> bool:
        """
        Check if the tool is allowed to run with the given arguments.
        
        Args:
            tool (Tool): The tool to be executed.
            **kwargs: Arguments passed to the tool.
            
        Returns:
            bool: True if allowed, False otherwise.
        """
        # Basic policy: Block HIGH risk tools (can be expanded later)
        if hasattr(tool, 'risk_level') and tool.risk_level == "HIGH":
            # For now, we block strict high risk. 
            # In future, we might ask for user confirmation here or in the Executor.
            return False
            
        return True

__all__ = ['SafetyPolicy', 'LegacySafetyPolicyAdapter', 'PolicyEngine', 'RiskPolicy', 'RateLimitPolicy', 'PermissionPolicy']

class LegacySafetyPolicyAdapter(SafetyPolicy):
    """
    Adapter to use the existing advanced SafetyPolicy from nova_ops.
    """
    def __init__(self, legacy_policy):
        self.legacy_policy = legacy_policy

    def check(self, tool: Tool, **kwargs) -> bool:
        # Map Tool object to name/args that legacy policy expects
        tool_name = tool.name
        # Note: legacy check_tool_permission returns (allowed, reason)
        allowed, reason = self.legacy_policy.check_tool_permission(tool_name, kwargs)
        if not allowed:
            # We could log the reason here or return it if we change Executor signature
            pass 
        return allowed


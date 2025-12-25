"""
Policy Engine for fine-grained control over tool execution.

Extends the basic SafetyPolicy to support multiple policy types:
- RiskPolicy: Blocks tools based on risk level
- RateLimitPolicy: Limits tool execution frequency
- PermissionPolicy: User/role-based permissions
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from src.nova_agents.tools.base import Tool


class Policy(ABC):
    """Abstract base class for all policies."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Policy identifier."""
        pass
    
    @abstractmethod
    def check(self, tool: Tool, **params) -> Tuple[bool, str]:
        """
        Check if tool execution should be allowed.
        
        Args:
            tool: Tool to check
            **params: Tool execution parameters
            
        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        pass


class RiskPolicy(Policy):
    """Policy that blocks tools based on risk level."""
    
    RISK_LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    
    def __init__(self, max_risk_level: str = "HIGH"):
        """
        Initialize with maximum allowed risk level.
        
        Args:
            max_risk_level: Maximum risk level to allow (LOW, MEDIUM, HIGH, CRITICAL)
        """
        if max_risk_level not in self.RISK_LEVELS:
            raise ValueError(f"Invalid risk level: {max_risk_level}")
        self.max_risk_level = max_risk_level
        self.max_risk_index = self.RISK_LEVELS.index(max_risk_level)
    
    @property
    def name(self) -> str:
        return "risk_policy"
    
    def check(self, tool: Tool, **params) -> Tuple[bool, str]:
        """Check if tool's risk level is within allowed threshold."""
        tool_risk = getattr(tool, 'risk_level', 'MEDIUM')
        try:
            tool_risk_index = self.RISK_LEVELS.index(tool_risk)
        except ValueError:
            # Unknown risk level, default to MEDIUM
            tool_risk_index = 1
        
        if tool_risk_index > self.max_risk_index:
            return False, f"Tool risk level '{tool_risk}' exceeds maximum '{self.max_risk_level}'"
        
        return True, "Risk level acceptable"


class RateLimitPolicy(Policy):
    """Policy that limits how often tools can be executed."""
    
    def __init__(self, max_calls_per_minute: int = 60):
        """
        Initialize with rate limit.
        
        Args:
            max_calls_per_minute: Maximum calls allowed per tool per minute
        """
        self.max_calls = max_calls_per_minute
        self.call_history: Dict[str, List[datetime]] = defaultdict(list)
    
    @property
    def name(self) -> str:
        return "rate_limit_policy"
    
    def check(self, tool: Tool, **params) -> Tuple[bool, str]:
        """Check if tool hasn't exceeded rate limit."""
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)
        
        # Clean old entries
        tool_name = tool.name
        self.call_history[tool_name] = [
            ts for ts in self.call_history[tool_name] if ts > cutoff
        ]
        
        # Check limit
        if len(self.call_history[tool_name]) >= self.max_calls:
            return False, f"Rate limit exceeded: {self.max_calls} calls/min"
        
        # Record this call
        self.call_history[tool_name].append(now)
        return True, "Rate limit OK"


class PermissionPolicy(Policy):
    """Policy that enforces user/role-based permissions."""
    
    def __init__(self, user_role: str = "user"):
        """
        Initialize with user role.
        
        Args:
            user_role: User's role (admin, user, guest)
        """
        self.user_role = user_role
        self.role_hierarchy = ["guest", "user", "admin"]
        self.tool_requirements: Dict[str, str] = {}  # tool_name -> required_role
    
    @property
    def name(self) -> str:
        return "permission_policy"
    
    def set_tool_requirement(self, tool_name: str, required_role: str):
        """Set minimum role required for a tool."""
        self.tool_requirements[tool_name] = required_role
    
    def check(self, tool: Tool, **params) -> Tuple[bool, str]:
        """Check if user has sufficient permissions."""
        required_role = self.tool_requirements.get(tool.name, "guest")
        
        try:
            user_level = self.role_hierarchy.index(self.user_role)
            required_level = self.role_hierarchy.index(required_role)
        except ValueError:
            return False, "Invalid role configuration"
        
        if user_level < required_level:
            return False, f"Insufficient permissions: requires '{required_role}', user is '{self.user_role}'"
        
        return True, "Permissions OK"


class PolicyEngine:
    """
    Orchestrates multiple policies for comprehensive control.
    
    Policies are checked in order, and all must pass for tool execution.
    """
    
    def __init__(self):
        self.policies: List[Policy] = []
    
    def add_policy(self, policy: Policy):
        """Add a policy to the engine."""
        self.policies.append(policy)
    
    def remove_policy(self, policy_name: str):
        """Remove a policy by name."""
        self.policies = [p for p in self.policies if p.name != policy_name]
    
    def check(self, tool: Tool, **params) -> Tuple[bool, str]:
        """
        Check tool against all policies.
        
        Returns:
            Tuple of (allowed, reason). If blocked, reason explains which policy failed.
        """
        for policy in self.policies:
            allowed, reason = policy.check(tool, **params)
            if not allowed:
                return False, f"[{policy.name}] {reason}"
        
        return True, "All policies passed"
    
    def get_active_policies(self) -> List[str]:
        """Get names of all active policies."""
        return [p.name for p in self.policies]

"""
Base Capability class for grouping tools into higher-level behaviors.

Capabilities represent intent-level skills that compose multiple tools to achieve complex goals.
Examples: CodingCapability (uses file tools + git), ResearchCapability (uses web tools + knowledge store).
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from src.nova_agents.tools.registry import ToolRegistry


class Capability(ABC):
    """
    Abstract base class for capabilities.
    
    A Capability groups related tools and provides high-level methods for complex operations.
    Unlike Tools (atomic operations), Capabilities orchestrate multiple tools.
    """
    
    def __init__(self, registry: ToolRegistry):
        """
        Initialize capability with access to the tool registry.
        
        Args:
            registry: ToolRegistry instance to access registered tools
        """
        self.registry = registry
        self._required_tools: List[str] = []
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this capability."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what this capability does."""
        pass
    
    @property
    def required_tools(self) -> List[str]:
        """List of tool names this capability depends on."""
        return self._required_tools
    
    def validate_dependencies(self) -> bool:
        """
        Check if all required tools are available in the registry.
        
        Returns:
            bool: True if all dependencies are met, False otherwise
        """
        available_tools = self.registry.list()
        missing = [tool for tool in self._required_tools if tool not in available_tools]
        if missing:
            print(f"[WARNING] Capability '{self.name}' missing tools: {missing}")
            return False
        return True
    
    @abstractmethod
    def execute(self, intent: str, **kwargs) -> Dict[str, Any]:
        """
        Execute the capability based on user intent.
        
        Args:
            intent: High-level description of what to do
            **kwargs: Additional parameters specific to this capability
            
        Returns:
            Dict containing execution results
        """
        pass


class BaseCapability(Capability):
    """Alias for backward compatibility."""
    pass

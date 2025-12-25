from abc import ABC, abstractmethod
from typing import Any, Dict

class Tool(ABC):
    """
    Abstract base class for all tools in the Nova platform.
    Every tool must implement this interface to be registered and executed.
    """
    name: str
    description: str
    risk_level: str  # LOW | MEDIUM | HIGH

    args_schema: Any = None # Pydantic model for arguments

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """
        Execute the tool's core logic.
        
        Args:
            **kwargs: Dynamic arguments required by the tool.
            
        Returns:
            Any: The result of the tool execution.
        """
        pass

class FunctionTool(Tool):
    """
    Wrapper for function-based tools to make them compatible with the Tool interface.
    """
    def __init__(self, name: str, func: callable, description: str, risk_level: str = "MEDIUM", args_schema: Any = None):
        self._name = name
        self._func = func
        self._description = description
        self.risk_level = risk_level
        self.args_schema = args_schema

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    def execute(self, **kwargs) -> Any:
        return self._func(**kwargs)

# Backward compatibility
BaseTool = Tool


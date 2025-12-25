from abc import ABC, abstractmethod
from typing import Optional, Any

class BaseTool(ABC):
    """
    Abstract base class for all ADK tools.
    """
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        """
        Execute the tool's main logic.
        
        Args:
            **kwargs: Arbitrary keyword arguments needed for execution.
            
        Returns:
            Any: The result of the tool execution.
        """
        pass

from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTool(ABC):
    """Abstract base class for all tools."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name (e.g., 'file.read')."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description for the model."""
        pass

    @abstractmethod
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with given arguments."""
        pass

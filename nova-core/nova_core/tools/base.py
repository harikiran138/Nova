from abc import ABC, abstractmethod
from typing import Dict, Any, Type
from pydantic import BaseModel

class BaseTool(ABC):
    """Abstract base class for all tools."""
    
    name: str
    description: str
    args_schema: Type[BaseModel]
    
    @abstractmethod
    def run(self, **kwargs) -> Any:
        """Execute the tool."""
        pass
        
    def to_schema(self) -> Dict[str, Any]:
        """Convert tool to JSON schema for the model."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.args_schema.model_json_schema()
            }
        }

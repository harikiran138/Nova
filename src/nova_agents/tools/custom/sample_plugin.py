"""
Sample plugin tool to demonstrate the plugin system.

This tool can be loaded dynamically via PluginLoader.
"""

from typing import Dict, Any
from src.nova_agents.tools.base import Tool


class WeatherTool(Tool):
    """Example plugin tool for weather information."""
    
    @property
    def name(self) -> str:
        return "weather.get"
    
    @property
    def description(self) -> str:
        return "Get weather information for a location (mock implementation)"
    
    @property
    def risk_level(self) -> str:
        return "LOW"
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Get weather for a location.
        
        Args:
            location: City or location name
            
        Returns:
            Mock weather data
        """
        location = kwargs.get("location", "Unknown")
        return {
            "success": True,
            "location": location,
            "temperature": 72,
            "conditions": "Sunny",
            "humidity": 45
        }


class CalculatorTool(Tool):
    """Example plugin tool for calculations."""
    
    @property
    def name(self) -> str:
        return "math.calculate"
    
    @property
    def description(self) -> str:
        return "Perform mathematical calculations"
    
    @property
    def risk_level(self) -> str:
        return "LOW"
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Perform calculation.
        
        Args:
            expression: Mathematical expression to evaluate
            
        Returns:
            Calculation result
        """
        expression = kwargs.get("expression", "0")
        try:
            # Safe eval with limited scope
            result = eval(expression, {"__builtins__": {}}, {})
            return {"success": True, "result": result, "expression": expression}
        except Exception as e:
            return {"success": False, "error": str(e)}

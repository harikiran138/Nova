from typing import Optional
from src.agent_core.agent_loop import AgentLoop
from src.agent_core.model_client import OllamaClient
from src.agent_core.tools.registry import ToolRegistry

class BaseAgent:
    """Base class for specialized agents."""
    
    def __init__(self, name: str, client: OllamaClient, tools: ToolRegistry, profile: str = "general"):
        self.name = name
        self.client = client
        self.tools = tools
        self.loop = AgentLoop(client, tools, profile_name=profile)
        
    def run(self, goal: str) -> str:
        """Run the agent on a goal."""
        return self.loop.process_input(goal)

from typing import Dict, Any
from .agent_loop import AgentLoop
from .tools.registry import ToolRegistry
from .config import Config

class MultiAgentManager:
    """Orchestrates specialized agents."""
    
    def __init__(self, tools: ToolRegistry):
        self.tools = tools
        self.config = Config.from_env()
        self.agents: Dict[str, AgentLoop] = {}

    def get_agent(self, role: str) -> AgentLoop:
        """Get or create a specialized agent."""
        if role not in self.agents:
            # Determine sandbox mode based on role
            sandbox_mode = True
            if role in ["security", "coder"]:
                sandbox_mode = True # Strict sandbox for risky agents
            elif role in ["research", "fixer"]:
                sandbox_mode = False # Read-only or safe ops
                
            self.agents[role] = AgentLoop(
                client=None, # Client is injected by factory or main loop
                tools=self.tools,
                profile_name=role,
                sandbox_mode=sandbox_mode
            )
        return self.agents[role]

    def dispatch(self, task: str) -> str:
        """Route task to appropriate agent (Simple Keyword Router)."""
        task_lower = task.lower()
        if "scan" in task_lower or "hack" in task_lower or "vulnerability" in task_lower:
            return "security"
        elif "code" in task_lower or "function" in task_lower or "refactor" in task_lower:
            return "coder"
        elif "research" in task_lower or "find" in task_lower or "search" in task_lower:
            return "research"
        elif "fix" in task_lower or "debug" in task_lower:
            return "fixer"
        else:
            return "general"

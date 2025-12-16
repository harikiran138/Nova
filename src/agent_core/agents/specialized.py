from .base_agent import BaseAgent

class SupervisorAgent(BaseAgent):
    """Orchestrates other agents."""
    def __init__(self, client, tools):
        super().__init__("Supervisor", client, tools, profile="general")
        # Supervisor specific logic can be added here
        # e.g., specialized system prompt to delegate tasks

class CoderAgent(BaseAgent):
    """Specialized in writing code."""
    def __init__(self, client, tools):
        super().__init__("Coder", client, tools, profile="coder")

class ResearcherAgent(BaseAgent):
    """Specialized in research."""
    def __init__(self, client, tools):
        super().__init__("Researcher", client, tools, profile="researcher")

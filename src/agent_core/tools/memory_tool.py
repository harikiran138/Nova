from typing import List
from ..memory import MemoryManager

class MemoryTool:
    """Tool for remembering facts."""
    
    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager
        self.name = "memory"
        self.description = "Remember a fact or preference for future use."

    def remember(self, fact: str) -> str:
        """Save a fact to long-term memory."""
        self.memory.add_fact(fact)
        return f"Fact remembered: {fact}"

    def recall(self) -> str:
        """List all learned facts."""
        facts = self.memory.get_facts()
        return "\n".join(facts) if facts else "No facts learned yet."

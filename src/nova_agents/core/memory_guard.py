"""
Memory Guard for multi-turn conversation tasks.

Maintains context and prevents drift in multi-turn interactions.
"""

from typing import List, Dict, Any
from collections import deque


class ConversationMemoryGuard:
    """
    Guards conversation context in multi-turn tasks.
    
    Prevents context drift by maintaining and summarizing conversation history.
    """
    
    def __init__(self, max_turns: int = 10, summary_threshold: int = 5):
        """
        Initialize memory guard.
        
        Args:
            max_turns: Maximum turns to keep in full detail
            summary_threshold: Number of turns before summarization
        """
        self.max_turns = max_turns
        self.summary_threshold = summary_threshold
        self.turns = deque(maxlen=max_turns)
        self.summary = None
    
    def add_turn(self, role: str, content: str):
        """Add a conversation turn."""
        self.turns.append({
            "role": role,
            "content": content
        })
        
        # Trigger summarization if needed
        if len(self.turns) >= self.summary_threshold and not self.summary:
            self._create_summary()
    
    def _create_summary(self):
        """Create summary of older turns."""
        if len(self.turns) < 3:
            return
        
        # Summarize first half of turns
        mid_point = len(self.turns) // 2
        turns_to_summarize = list(self.turns)[:mid_point]
        
        summary_points = []
        for turn in turns_to_summarize:
            if turn["role"] == "user":
                summary_points.append(f"User asked: {turn['content'][:50]}...")
            else:
                summary_points.append(f"Assistant responded: {turn['content'][:50]}...")
        
        self.summary = "\n".join(summary_points)
    
    def get_context_prompt(self, current_prompt: str) -> str:
        """
        Get prompt with conversation context prepended.
        
        Args:
            current_prompt: Current user prompt
            
        Returns:
            Prompt with context
        """
        if not self.turns:
            return current_prompt
        
        context_parts = []
        
        # Add summary if exists
        if self.summary:
            context_parts.append(f"Earlier context:\n{self.summary}\n")
        
        # Add recent turns (last 2-3)
        recent_turns = list(self.turns)[-3:]
        if recent_turns:
            context_parts.append("Recent conversation:")
            for turn in recent_turns:
                role = "User" if turn["role"] == "user" else "You"
                context_parts.append(f"{role}: {turn['content']}")
        
        # Add current prompt
        context_parts.append(f"\nCurrent question: {current_prompt}")
        
        return "\n".join(context_parts)
    
    def get_last_user_input(self) -> str:
        """Get the last user input."""
        for turn in reversed(self.turns):
            if turn["role"] == "user":
                return turn["content"]
        return ""
    
    def get_last_assistant_response(self) -> str:
        """Get the last assistant response."""
        for turn in reversed(self.turns):
            if turn["role"] == "assistant":
                return turn["content"]
        return ""
    
    def reset(self):
        """Reset conversation memory."""
        self.turns.clear()
        self.summary = None
    
    def get_turn_count(self) -> int:
        """Get number of turns in memory."""
        return len(self.turns)
    
    def has_context(self) -> bool:
        """Check if there is conversation context."""
        return len(self.turns) > 0

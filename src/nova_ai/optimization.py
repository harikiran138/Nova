from typing import List, Dict
import re

class ContextCompressor:
    """Compresses conversation history to save tokens."""
    
    def __init__(self, ollama_client=None):
        self.client = ollama_client

    def compress(self, history: List[Dict[str, str]], max_tokens: int = 4000) -> List[Dict[str, str]]:
        """
        Compresses history if it exceeds heuristics.
        Simple strategy: Keep system prompt + last N messages + summary of middle.
        """
        if len(history) <= 10:
            return history
            
        system_prompts = [m for m in history if m['role'] == 'system']
        recent_messages = history[-5:] # Keep last 5 turns intact
        
        middle_messages = history[len(system_prompts):-5]
        
        if not middle_messages:
            return history
            
        # Create summary of middle messages
        summary_text = self._summarize(middle_messages)
        
        summary_message = {
            "role": "system", 
            "content": f"[Previous Context Summary]: {summary_text}"
        }
        
        return system_prompts + [summary_message] + recent_messages

    def _summarize(self, messages: List[Dict[str, str]]) -> str:
        """Summarize a list of messages."""
        text_blob = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        
        if self.client:
            try:
                # Use a fast model for summarization
                prompt = f"""
                Summarize the following conversation key points in 3-5 sentences.
                Focus on:
                1. The main goal discussed.
                2. Key information discovered.
                3. Successful tool executions.
                4. Final conclusions reached.
                
                CONVERSATION:
                {text_blob}
                """
                return self.client.generate([], prompt, model="gemma:2b") 
            except:
                pass
        
        # Fallback: Truncate
        return f"... {len(messages)} preserved messages ..."

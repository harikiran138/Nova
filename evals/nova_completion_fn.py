"""
Nova Completion Function - Standalone version for evals.

This is a simplified adapter that doesn't require the full OpenAI Evals framework.
"""

import sys
from pathlib import Path
from typing import Any, Union, List, Dict

# Add Nova to path
sys.path.append(str(Path(__file__).parent.parent))

from src.nova_shared.config import Config
from src.nova_agents.tools.registry import ToolRegistry
from src.nova_ai.model_client import OllamaClient
from src.nova_agents.agent_loop import AgentLoop


class NovaCompletionFn:
    """
    Completion function that uses Nova's AgentLoop.
    
    Simplified standalone version for evaluations.
    """
    
    def __init__(self, model: str = None):
        """
        Initialize Nova completion function.
        
        Args:
            model: Model name (will use Nova's configured model if not specified)
        """
        # Initialize Nova components
        self.config = Config.from_env()
        self.model = model or self.config.ollama_model
        
        # Create model client
        self.client = OllamaClient(
            model=self.model,
            base_url=self.config.ollama_base_url
        )
        
        # Create tool registry
        self.registry = ToolRegistry(
            workspace_dir=self.config.workspace_dir,
            allow_shell=self.config.allow_shell_commands,
            offline_mode=self.config.offline_mode
        )
        
        # Create agent
        self.agent = AgentLoop(
            client=self.client,
            tools=self.registry,
            profile_name="general",
            sandbox_mode=False
        )
    
    def __call__(self, prompt: Union[str, List[Dict[str, str]]]) -> str:
        """
        Run Nova on the given prompt.
        
        Args:
            prompt: Eval prompt (can be string or messages list)
            
        Returns:
            Nova's response as a string
        """
        # Convert prompt to string
        if isinstance(prompt, str):
            query = prompt
        elif isinstance(prompt, list):
            # Messages format
            query = "\n".join([
                f"{msg.get('role', 'user')}: {msg.get('content', '')}"
                for msg in prompt
            ])
        else:
            query = str(prompt)
        
        # Run Nova
        try:
            # Reset conversation for clean eval
            self.agent.conversation_history = []
            response = self.agent.process_input(query)
            return response
            
        except Exception as e:
            error_msg = f"Nova execution error: {str(e)}"
            print(f"[ERROR] {error_msg}")
            return error_msg


def get_nova_completion_fn(model: str = None):
    """
    Factory function to create Nova completion function.
    
    Args:
        model: Model name
        
    Returns:
        NovaCompletionFn instance
    """
    return NovaCompletionFn(model=model)

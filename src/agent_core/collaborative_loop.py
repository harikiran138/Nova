from typing import List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from .agent_loop import AgentLoop
from .model_client import OllamaClient
from .gemini_client import GeminiClient
from .tools import ToolRegistry

console = Console()

class CollaborativeLoop:
    """Orchestrates collaboration between two AI models."""
    
    def __init__(self, primary_client, secondary_client, tools: ToolRegistry):
        self.primary = primary_client
        self.secondary = secondary_client
        self.tools = tools
        
        # Initialize the executing agent (Primary drives the tools)
        self.agent = AgentLoop(self.primary, self.tools, profile_name="collaborator")

    def run_duo(self, goal: str):
        """Run the collaborative workflow."""
        console.print(Panel(f"[bold]Goal:[/bold] {goal}", title="🤝 Duo Mode Started", border_style="magenta"))
        
        # 1. Primary proposes a plan
        console.print(f"[bold cyan]{self._get_name(self.primary)} (Primary):[/bold cyan] Proposing plan...")
        plan_prompt = f"Goal: {goal}\nPropose a detailed step-by-step plan to achieve this goal. Do not execute yet."
        plan = self.primary.generate([{"role": "user", "content": plan_prompt}])
        console.print(Panel(plan, title="Initial Plan", border_style="cyan"))
        
        # 2. Secondary critiques
        console.print(f"[bold green]{self._get_name(self.secondary)} (Secondary):[/bold green] Reviewing plan...")
        critique_prompt = f"Goal: {goal}\nPrimary Agent's Plan:\n{plan}\n\nCritique this plan. Identify potential risks, missing steps, or optimizations. Be constructive."
        critique = self.secondary.generate([{"role": "user", "content": critique_prompt}])
        console.print(Panel(critique, title="Peer Review", border_style="green"))
        
        # 3. Primary refines and executes
        console.print(f"[bold cyan]{self._get_name(self.primary)} (Primary):[/bold cyan] Refining and executing...")
        execution_prompt = f"Goal: {goal}\nMy Initial Plan:\n{plan}\n\nPeer Review:\n{critique}\n\nBased on the review, refine the plan and EXECUTE it using your tools. Start immediately."
        
        # We inject this context into the agent's history and let it run
        self.agent.process_input(execution_prompt)

    def _get_name(self, client) -> str:
        if isinstance(client, GeminiClient):
            return "Gemini"
        elif isinstance(client, OllamaClient):
            return f"Ollama ({client.model})"
        return "Agent"

#!/usr/bin/env python3
"""
Prompt Refiner AI
A small tool to optimize user prompts for better LLM results.
"""

import sys
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

# Add src to path to reuse Nova's client
sys.path.append(str(Path(__file__).parent / "src"))

from agent_core.config import Config
from agent_core import OllamaClient

console = Console()

def refine_prompt(client, raw_prompt: str) -> str:
    """Refine the prompt using expert prompt engineering techniques."""
    
    meta_prompt = f"""
    You are an expert Prompt Engineer and AI Optimizer.
    Your task is to rewrite the user's raw prompt to make it clear, specific, and highly effective for an LLM.
    
    Follow this structure for the refined prompt:
    1. **Persona**: Assign a specific role (e.g., "Act as a Senior Python Developer").
    2. **Context**: Add necessary background or assumptions.
    3. **Task**: Clearly state the objective.
    4. **Constraints**: List any limitations or rules.
    5. **Format**: Specify how the output should look (e.g., "Markdown code blocks").
    
    USER RAW PROMPT:
    "{raw_prompt}"
    
    OUTPUT ONLY THE REFINED PROMPT. DO NOT ADD EXPLANATIONS.
    """
    
    try:
        messages = [{"role": "user", "content": meta_prompt}]
        return client.generate(messages)
    except Exception as e:
        return f"Error generating prompt: {e}"

def main():
    console.print(Panel.fit(
        "[bold magenta]✨ Prompt Refiner AI[/bold magenta]\n"
        "[dim]Turn simple ideas into powerful prompts.[/dim]",
        border_style="magenta"
    ))
    
    # Load Config
    try:
        config = Config.from_env()
        # Ensure model is valid or fallback
        model = config.ollama_model or "llama3"
        client = OllamaClient(config.ollama_base_url, model)
    except Exception as e:
        console.print(f"[red]Error initializing AI client: {e}[/red]")
        return

    while True:
        try:
            user_input = Prompt.ask("\n[bold cyan]Enter your raw prompt[/bold cyan] (or 'exit')")
        except EOFError:
            break
            
        if user_input.lower() in ['exit', 'quit']:
            break
            
        if not user_input.strip():
            continue
            
        with console.status("[bold magenta]Refining your prompt...[/bold magenta]"):
            refined = refine_prompt(client, user_input)
            
        if refined and not refined.startswith("Error"):
            console.print("\n[bold green]✨ Refined Prompt:[/bold green]")
            console.print(Panel(refined, border_style="green"))
            
            if Prompt.ask("\nCopy to clipboard?", choices=["y", "n"], default="y") == "y":
                import subprocess
                try:
                    process = subprocess.Popen('pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
                    process.communicate(refined.encode('utf-8'))
                    console.print("[dim]Copied to clipboard![/dim]")
                except:
                    console.print("[dim]Clipboard copy failed (pbcopy not found).[/dim]")
        else:
            console.print(f"[red]{refined or 'Unknown error occurred.'}[/red]")

if __name__ == "__main__":
    main()

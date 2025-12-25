"""Ollama API client for model inference."""

import json
import requests
from typing import List, Dict, Any, Optional
from rich.console import Console

console = Console()


class OllamaClient:
    """Client for interacting with Ollama API.
    
    Attributes:
        base_url: Base URL for Ollama API (e.g., http://127.0.0.1:11434)
        model: Model name to use for inference
    """
    
    def __init__(self, base_url: str, model: str):
        """Initialize Ollama client.
        
        Args:
            base_url: Base URL for Ollama API
            model: Model name to use
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.chat_endpoint = f"{self.base_url}/api/chat"
    
    def test_connection(self) -> bool:
        """Test connection to Ollama server.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[str]:
        """Generate a response from the Ollama model.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            system_prompt: Optional system prompt to prepend
            
        Returns:
            Generated response text, or None if error
        """
        # Prepend system prompt if provided
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,  # Use non-streaming for simplicity
        }
        
        # Add optional parameters like temperature, top_p, etc.
        # Filter strictly for valid Ollama parameters if strictness needed,
        # but passing kwargs usually works fine as Ollama ignores unknown fields or we trust caller.
        valid_options = ["temperature", "top_k", "top_p", "seed", "repeat_penalty", "stop"]
        options = {k: v for k, v in kwargs.items() if k in valid_options}
        if options:
            payload["options"] = options
            
        # Handle 'stop' specially if it's meant to be top-level or options-level.
        # Ollama API expects 'options' dict for 'temperature', 'stop' etc usually go in options or top level depending on version.
        # Recent Ollama API puts Modelfiles parameters in 'options'.
        # However, 'stream' and 'format' are top level.
        pass
        
        try:
            response = requests.post(
                self.chat_endpoint,
                json=payload,
                timeout=120,  # 2 minute timeout for generation
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("message", {}).get("content", "")
            
        except requests.exceptions.Timeout:
            console.print("[red]Error: Request timed out. The model may be processing a long response.[/red]")
            return None
        except requests.exceptions.ConnectionError:
            console.print(f"[red]Error: Cannot connect to Ollama at {self.base_url}[/red]")
            console.print("[yellow]Make sure Ollama is running:[/yellow]")
            console.print("  1. Check if Ollama is installed: ollama --version")
            console.print("  2. Start Ollama service if needed")
            console.print(f"  3. Pull the model if not available: ollama pull {self.model}")
            return None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                console.print(f"[red]Error: Model '{self.model}' not found[/red]")
                console.print(f"[yellow]Pull the model first: ollama pull {self.model}[/yellow]")
            else:
                console.print(f"[red]HTTP Error: {e}[/red]")
            return None
        except Exception as e:
            console.print(f"[red]Unexpected error: {e}[/red]")
            return None
    
    def get_available_models(self) -> List[str]:
        """Get list of available models from Ollama.
        
        Returns:
            List of model names
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except Exception:
            return []

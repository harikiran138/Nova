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
    
    def stream_generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ):
        """Streaming version of generate."""
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }
        
        valid_options = ["temperature", "top_k", "top_p", "seed", "repeat_penalty", "stop"]
        options = {k: v for k, v in kwargs.items() if k in valid_options}
        if options:
            payload["options"] = options
            
        try:
            # console.print(f"[dim]DEBUG: POST {self.chat_endpoint} with model {self.model}[/dim]")
            response = requests.post(
                self.chat_endpoint,
                json=payload,
                stream=True,
                timeout=120,
            )
            if response.status_code != 200:
                console.print(f"[red]Ollama Error {response.status_code}: {response.text}[/red]")
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if not chunk.get("done"):
                        yield chunk.get("message", {}).get("content", "")
                        
        except Exception as e:
            console.print(f"[red]Streaming Error: {e}[/red]")
            yield None

    def get_available_models(self) -> List[str]:
        """Get list of available models from Ollama."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except Exception:
            return []


class GeminiClient:
    """Client for Gemini API via direct REST calls."""
    
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-lite-preview-02-05"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    def test_connection(self) -> bool:
        return bool(self.api_key)

    def _prepare_payload(self, messages, system_prompt, **kwargs):
        contents = []
        system_instruction = None
        if system_prompt:
            system_instruction = {"parts": [{"text": system_prompt}]}

        for msg in messages:
            role = "user" if msg["role"] in ["user", "system"] else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": kwargs.get("temperature", 0.3),
                "topP": kwargs.get("top_p", 0.95),
                "maxOutputTokens": kwargs.get("max_tokens", 2048),
            }
        }
        if system_instruction:
            payload["system_instruction"] = system_instruction
        return payload

    def generate(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None, **kwargs: Any) -> Optional[str]:
        endpoint = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
        payload = self._prepare_payload(messages, system_prompt, **kwargs)
        try:
            response = requests.post(endpoint, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            if "candidates" in data and data["candidates"]:
                candidate = data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    return candidate["content"]["parts"][0]["text"]
            return None
        except Exception as e:
            console.print(f"[red]Gemini Error: {e}[/red]")
            return None

    def stream_generate(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None, **kwargs: Any):
        endpoint = f"{self.base_url}/models/{self.model}:streamGenerateContent?key={self.api_key}&alt=sse"
        payload = self._prepare_payload(messages, system_prompt, **kwargs)
        try:
            response = requests.post(endpoint, json=payload, stream=True, timeout=30)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode("utf-8")
                    if line_str.startswith("data: "):
                        data = json.loads(line_str[6:])
                        if "candidates" in data and data["candidates"]:
                            candidate = data["candidates"][0]
                            if "content" in candidate and "parts" in candidate["content"]:
                                yield candidate["content"]["parts"][0]["text"]
        except Exception as e:
            console.print(f"[red]Gemini Streaming Error: {e}[/red]")
            yield None

    def get_available_models(self) -> List[str]:
        return [self.model]

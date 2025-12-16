import requests
import json
from typing import List, Dict, Optional
from rich.console import Console

console = Console()

class OpenRouterClient:
    """Client for OpenRouter API (OpenAI-compatible)."""
    
    def __init__(self, api_key: str, model: str = "openai/gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://github.com/nova-agent", # Required by OpenRouter
            "X-Title": "Nova Agent", # Required by OpenRouter
            "Content-Type": "application/json"
        }

    def generate(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None, tools: Optional[List[Dict]] = None) -> Optional[str]:
        """Generate response from OpenRouter."""
        
        # Prepend system prompt if provided
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages
            
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2048,
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            # Extract text
            if "choices" in result and result["choices"]:
                choice = result["choices"][0]
                message = choice["message"]
                
                # Handle Tool Calls
                if message.get("tool_calls"):
                    # Convert OpenAI tool calls to Nova's JSON format
                    # Nova expects: {"tool": "name", "args": {...}}
                    # We pick the first tool call for simplicity in this loop
                    tool_call = message["tool_calls"][0]
                    func = tool_call["function"]
                    return json.dumps({
                        "tool": func["name"],
                        "args": json.loads(func["arguments"])
                    })
                
                return message["content"]
            
            return None
            
        except Exception as e:
            console.print(f"[red]OpenRouter API Error: {e}[/red]")
            if "response" in locals():
                console.print(f"[dim]{response.text}[/dim]")
            return None

    def test_connection(self) -> bool:
        """Test API key validity."""
        try:
            # Simple generation test with a cheap model
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": "Hi"}],
                "max_tokens": 5
            }
            res = requests.post(self.base_url, headers=self.headers, json=payload, timeout=10)
            return res.status_code == 200
        except:
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available models (Mocked or fetched)."""
        # OpenRouter has a /models endpoint but for simplicity we can just return the current one
        # or fetch from https://openrouter.ai/api/v1/models
        try:
            res = requests.get("https://openrouter.ai/api/v1/models", timeout=5)
            if res.status_code == 200:
                data = res.json()
                return [m["id"] for m in data.get("data", [])]
        except:
            pass
        return [self.model]

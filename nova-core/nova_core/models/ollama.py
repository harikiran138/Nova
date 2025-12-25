import requests
import json
from typing import List, Dict, Any, Optional, Generator
from ..config import config

class OllamaClient:
    """Client for interacting with Ollama API."""
    
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or config.ollama_base_url
        self.model = model or config.ollama_model
        self.chat_endpoint = f"{self.base_url}/api/chat"
        
    def generate(self, messages: List[Dict[str, str]], stream: bool = False) -> str | Generator[str, None, None]:
        """Generate a response from the model."""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": 0.7
            }
        }
        
        try:
            response = requests.post(self.chat_endpoint, json=payload, stream=stream, timeout=120)
            response.raise_for_status()
            
            if stream:
                return self._stream_response(response)
            else:
                return response.json().get("message", {}).get("content", "")
                
        except Exception as e:
            print(f"Error generating response: {e}")
            return None

    def _stream_response(self, response) -> Generator[str, None, None]:
        """Yield tokens from streaming response."""
        for line in response.iter_lines():
            if line:
                try:
                    json_response = json.loads(line)
                    content = json_response.get("message", {}).get("content", "")
                    if content:
                        yield content
                except json.JSONDecodeError:
                    pass

    def get_models(self) -> List[str]:
        """List available models."""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                return [m["name"] for m in response.json().get("models", [])]
        except Exception as e:
            print(f"Error getting models: {e}")
            pass
        return []

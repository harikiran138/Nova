import requests
import json
from typing import List, Dict, Optional
from rich.console import Console

console = Console()

class GeminiClient:
    """Client for Google Gemini API."""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    def generate(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> Optional[str]:
        """Generate response from Gemini."""
        
        # Convert OpenAI/Ollama format to Gemini format
        # Gemini uses "contents": [{"role": "user", "parts": [{"text": "..."}]}]
        # System prompt is usually passed as the first "user" message or via specific API field in newer versions.
        # For v1beta, we'll prepend system prompt to the first user message or use "system_instruction" if supported (v1beta supports it now).
        
        contents = []
        
        # Handle history
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
            
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 2048,
            }
        }
        
        if system_prompt:
             # Gemini 1.5 Pro/Flash supports system_instruction. Gemini 1.0 Pro might not.
             # Safe fallback: Prepend to first user message if model is old, but let's try system_instruction first.
             # Actually, for broad compatibility with the REST API, let's use the system_instruction field.
             payload["system_instruction"] = {
                 "parts": [{"text": system_prompt}]
             }

        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        
        import time
        import random
        
        max_retries = 3
        base_delay = 1
        
        for attempt in range(max_retries + 1):
            try:
                response = requests.post(url, json=payload, timeout=120)
                response.raise_for_status()
                
                result = response.json()
                # Extract text
                # Response format: candidates[0].content.parts[0].text
                if "candidates" in result and result["candidates"]:
                    candidate = result["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        return candidate["content"]["parts"][0]["text"]
                
                return None
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    if attempt < max_retries:
                        delay = (base_delay * (2 ** attempt)) + (random.random() * 0.5)
                        console.print(f"[yellow]Rate limit hit. Retrying in {delay:.1f}s...[/yellow]")
                        time.sleep(delay)
                        continue
                    else:
                        console.print(f"[red]Gemini Rate Limit Exceeded after {max_retries} retries.[/red]")
                        return None
                else:
                    console.print(f"[red]Gemini API Error: {e}[/red]")
                    return None
            except requests.exceptions.RequestException as e:
                console.print(f"[red]Gemini Network Error: {e}[/red]")
                return None
            except Exception as e:
                console.print(f"[red]Gemini API Error: {e}[/red]")
                if "response" in locals():
                    console.print(f"[dim]{response.text}[/dim]")
                return None

    def test_connection(self) -> bool:
        """Test API key validity."""
        # Simple generation test
        try:
            res = self.generate([{"role": "user", "content": "Hi"}])
            return res is not None
        except:
            return False

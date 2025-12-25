import os
import json
from typing import Any
from src.nova_agents.tools.base import Tool
from src.nova_ai.model_client import OllamaClient

A2UI_SYSTEM_PROMPT = """You are an A2UI (Agent-to-User Interface) expert.
Your goal is to generate a user interface definition based on the user's description.
Output MUST be a valid JSON object starting with {"root": ...} conforming to the A2UI schema.

Available component types:
- Container (props: style)
- Text (props: content, style)
- Button (props: label, style)
- Row (props: style)
- Column (props: style)
- Card (props: title, style)
- Image (props: src, alt, style)

Example Output:
{
  "root": {
    "type": "Card",
    "props": {
      "title": "Welcome"
    },
    "children": [
      {
        "type": "Text", 
        "props": {"content": "Hello A2UI", "style": {"fontSize": "18px"}}
      }
    ]
  }
}

Generate ONLY raw JSON. Do not wrap in markdown.
"""

class A2UITool(Tool):
    name = "generate_ui"
    description = "Generates a user interface (A2UI JSON) based on a text description. Use this when the user asks to 'show me a UI' or 'create an interface'."
    risk_level = "LOW"
    
    def execute(self, description: str, **kwargs) -> Any:
        try:
            model = os.getenv("OLLAMA_MODEL", "llama3")
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            
            client = OllamaClient(base_url=base_url, model=model)
            
            # If description is passed as a kwarg named 'query' or similar, handle it
            query = description or kwargs.get('query') or kwargs.get('input') or "Show a simple UI"
            
            response = client.generate(
                messages=[{"role": "user", "content": str(query)}],
                system_prompt=A2UI_SYSTEM_PROMPT,
                temperature=0.2
            )
            
            if response:
                clean = response.strip()
                # Remove markdown code blocks if present
                if clean.startswith("```json"):
                    clean = clean.split("```json")[1]
                    if "```" in clean:
                        clean = clean.split("```")[0]
                elif clean.startswith("```"):
                     clean = clean.split("```")[1]
                     if "```" in clean:
                        clean = clean.split("```")[0]
                return clean.strip()
                
            return '{"root": {"type": "Text", "props": {"content": "Error generating UI"}}}'
        except Exception as e:
            return f'{{"root": {{"type": "Text", "props": {{"content": "Exception: {str(e)}"}}}}}}'

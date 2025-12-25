import requests
from pydantic import BaseModel, Field
from nova_core.tools.base import BaseTool

class WebGetArgs(BaseModel):
    url: str = Field(..., description="URL to fetch")

class WebGetTool(BaseTool):
    name = "web_get"
    description = "Fetch the text content of a webpage."
    args_schema = WebGetArgs
    
    def run(self, url: str) -> str:
        try:
            response = requests.get(url, timeout=10)
            return response.text[:5000]  # Truncate for now
        except Exception as e:
            return f"Error fetching URL: {e}"

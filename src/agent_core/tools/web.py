import requests
import re
from typing import Dict, Any
from .base import BaseTool

class WebGetTool(BaseTool):
    @property
    def name(self) -> str:
        return "web.get"

    @property
    def description(self) -> str:
        return "web.get(url) - Fetch content from a URL"

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        url = args.get("url", "")
        if not url:
            return {"success": False, "error": "Missing required argument: url"}
        
        if not url.startswith(("http://", "https://")):
            return {"success": False, "error": "URL must start with http:// or https://"}
        
        try:
            headers = {"User-Agent": "Mozilla/5.0 (compatible; NovaAgent/1.0)"}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            content = response.text
            content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
            content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
            content = re.sub(r'<[^>]+>', '', content)
            content = re.sub(r'\n\s*\n', '\n\n', content)
            content = content.strip()
            
            max_length = 5000
            if len(content) > max_length:
                content = content[:max_length] + "\n\n[Content truncated...]"
            
            return {"success": True, "result": content}
        except Exception as e:
            return {"success": False, "error": f"Error fetching URL: {str(e)}"}

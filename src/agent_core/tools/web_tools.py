from typing import Dict, Any, List
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from .base import BaseTool

class WebSearchTool(BaseTool):
    def __init__(self):
        self._ddgs = DDGS()

    @property
    def name(self) -> str:
        return "web.search"

    @property
    def description(self) -> str:
        return "web.search(query) - Search the web using DuckDuckGo. Returns top 5 results."

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        query = args.get("query", "")
        if not query:
            return {"success": False, "error": "Missing query"}

        import time
        for attempt in range(3):
            try:
                # Re-init DDGS to encourage fresh session
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=5, backend="lite"))
                    return {"success": True, "result": results}
            except Exception as e:
                if "202" in str(e) or "Ratelimit" in str(e):
                    print(f"Server 202/Ratelimit hit. Retrying in {2**attempt}s...")
                    time.sleep(2 ** attempt)
                else:
                    return {"success": False, "error": f"Search failed: {str(e)}"}
        
        return {"success": False, "error": "Search failed after 3 retries due to ratelimiting."}

class WebExtractTool(BaseTool):
    @property
    def name(self) -> str:
        return "web.extract"

    @property
    def description(self) -> str:
        return "web.extract(url) - Extract main text content from a URL."

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        url = args.get("url", "")
        if not url:
            return {"success": False, "error": "Missing url"}

        try:
            # User-Agent to avoid blocking
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove scripts and styles
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
                
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Limit length to avoid context overflow (approx 4000 chars)
            return {"success": True, "result": text[:4000]}
            
        except Exception as e:
            return {"success": False, "error": f"Extraction failed: {str(e)}"}

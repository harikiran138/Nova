"""
Research Capability - Web search, extraction, and knowledge synthesis.

This capability groups web-related tools to provide high-level research operations.
"""

from typing import Dict, List, Any
from src.nova_agents.capabilities.base import Capability
from src.nova_agents.tools.registry import ToolRegistry


class ResearchCapability(Capability):
    """
    Capability for conducting web research and knowledge extraction.
    
    Composes: web.search, web.extract, web.learn_topic
    """
    
    def __init__(self, registry: ToolRegistry):
        super().__init__(registry)
        self._required_tools = ["web.search", "web.extract", "web.learn_topic"]
    
    @property
    def name(self) -> str:
        return "research"
    
    @property
    def description(self) -> str:
        return "Conduct web research, extract information, and synthesize knowledge on topics"
    
    def execute(self, intent: str, **kwargs) -> Dict[str, Any]:
        """
        Execute research based on intent.
        
        Args:
            intent: Research goal (e.g., "learn about quantum computing")
            **kwargs: Optional parameters:
                - query: Search query override
                - depth: "quick" or "deep" (default: "quick")
                - extract_urls: List of URLs to extract content from
        
        Returns:
            Dict with research results
        """
        if not self.validate_dependencies():
            return {"success": False, "error": "Missing required tools"}
        
        depth = kwargs.get("depth", "quick")
        results = {"success": True, "sources": [], "summary": ""}
        
        try:
            # Step 1: Search
            query = kwargs.get("query", intent)
            search_tool = self.registry.get("web.search")
            search_result = search_tool.execute(query=query)
            
            if not search_result.get("success"):
                return {"success": False, "error": "Search failed"}
            
            results["sources"] = search_result.get("results", [])
            
            # Step 2: Deep dive if requested
            if depth == "deep":
                learn_tool = self.registry.get("web.learn_topic")
                learn_result = learn_tool.execute(topic=intent)
                results["summary"] = learn_result.get("summary", "")
            else:
                # Quick summary from search results
                results["summary"] = f"Found {len(results['sources'])} sources on '{intent}'"
            
            return results
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def extract_from_urls(self, urls: List[str]) -> Dict[str, Any]:
        """
        Extract content from a list of URLs.
        
        Args:
            urls: List of URLs to extract
            
        Returns:
            Dict with extracted content
        """
        if not self.validate_dependencies():
            return {"success": False, "error": "Missing required tools"}
        
        extract_tool = self.registry.get("web.extract")
        results = []
        
        for url in urls:
            try:
                result = extract_tool.execute(url=url)
                if result.get("success"):
                    results.append({
                        "url": url,
                        "content": result.get("content", ""),
                        "title": result.get("title", "")
                    })
            except Exception as e:
                results.append({"url": url, "error": str(e)})
        
        return {"success": True, "extractions": results}

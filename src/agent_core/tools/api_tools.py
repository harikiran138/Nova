from typing import Dict, Any
from .base import BaseTool

class WolframAlphaTool(BaseTool):
    @property
    def name(self) -> str:
        return "wolfram_alpha"
    @property
    def description(self) -> str:
        return "wolfram_alpha(query) - Query Wolfram Alpha (Requires API Key)"
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": False, "error": "Wolfram Alpha API Key not configured."}

class SpotifySearchTool(BaseTool):
    @property
    def name(self) -> str:
        return "spotify_search"
    @property
    def description(self) -> str:
        return "spotify_search(query) - Search Spotify (Requires API Key)"
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": False, "error": "Spotify API Key not configured."}

class DalleImageGenerateTool(BaseTool):
    @property
    def name(self) -> str:
        return "dalle_image_generate"
    @property
    def description(self) -> str:
        return "dalle_image_generate(prompt) - Generate image (Requires OpenAI Key)"
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": False, "error": "OpenAI API Key not configured."}

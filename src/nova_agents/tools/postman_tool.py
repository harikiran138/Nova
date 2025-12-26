import os
import requests
from typing import Any, Dict, List, Optional
from src.nova_agents.tools.base import Tool

class PostmanTool(Tool):
    """
    Integrates with Postman API to manage Collections, Environments, and run Monitors.
    """
    name = "postman_tool"
    description = "Interact with Postman: list/get collections, manage environments, run monitors."
    risk_level = "LOW"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Postman tool.
        
        Args:
            api_key: Postman API Key (default: POSTMAN_API_KEY env var)
        """
        self.api_key = api_key or os.environ.get("POSTMAN_API_KEY")
        self.base_url = "https://api.getpostman.com"
        
        if not self.api_key:
            print("Warning: POSTMAN_API_KEY not found. Tool will likely fail if not provided in execute.")

    def execute(self, command: str, **kwargs) -> Any:
        """
        Execute Postman commands.
        
        Args:
            command: The action to perform (list_collections, get_collection, list_environments, list_workspaces)
            **kwargs: Additional arguments for the specific command.
        """
        if not self.api_key:
             return {"success": False, "error": "Missing POSTMAN_API_KEY. Please set it in .env or provide it."}

        headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

        try:
            if command == "list_collections":
                return self._list_collections(headers)
            elif command == "get_collection":
                collection_id = kwargs.get("collection_id")
                if not collection_id:
                     return {"success": False, "error": "collection_id is required"}
                return self._get_collection(headers, collection_id)
            elif command == "list_environments":
                return self._list_environments(headers)
            elif command == "list_workspaces":
                return self._list_workspaces(headers)
            else:
                return {"success": False, "error": f"Unknown command: {command}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _list_collections(self, headers: Dict) -> Dict:
        resp = requests.get(f"{self.base_url}/collections", headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return {"success": True, "collections": data.get("collections", [])}

    def _get_collection(self, headers: Dict, collection_id: str) -> Dict:
        resp = requests.get(f"{self.base_url}/collections/{collection_id}", headers=headers)
        resp.raise_for_status()
        return {"success": True, "collection": resp.json().get("collection")}

    def _list_environments(self, headers: Dict) -> Dict:
        resp = requests.get(f"{self.base_url}/environments", headers=headers)
        resp.raise_for_status()
        return {"success": True, "environments": resp.json().get("environments", [])}
        
    def _list_workspaces(self, headers: Dict) -> Dict:
        resp = requests.get(f"{self.base_url}/workspaces", headers=headers)
        resp.raise_for_status()
        return {"success": True, "workspaces": resp.json().get("workspaces", [])}

import os
import requests
from typing import Any, Dict, List, Optional
from src.nova_agents.tools.base import Tool

class PostHogTool(Tool):
    """
    Integrates with PostHog API to manage projects, feature flags, and insights.
    Mimics the capabilities of the PostHog MCP server but runs natively in Nova.
    """
    name = "posthog_tool"
    description = "Interact with PostHog analytics: list projects, feature flags, query insights, and annotations."
    risk_level = "LOW"

    def __init__(self, api_key: Optional[str] = None, host: str = "us"):
        """
        Initialize PostHog tool.
        
        Args:
            api_key: Personal API Key (default: POSTHOG_API_KEY env var)
            host: 'us' (https://us.posthog.com) or 'eu' (https://eu.posthog.com)
        """
        self.api_key = api_key or os.environ.get("POSTHOG_API_KEY")
        self.base_url = "https://eu.posthog.com" if host == "eu" else "https://us.posthog.com"
        
        if not self.api_key:
            print("Warning: POSTHOG_API_KEY not found. Tool will likely fail if not provided in execute.")

    def execute(self, command: str, **kwargs) -> Any:
        """
        Execute PostHog commands.
        
        Args:
            command: The action to perform (list_projects, list_feature_flags, get_insight, create_annotation)
            **kwargs: Additional arguments for the specific command.
        """
        if not self.api_key:
             return {"success": False, "error": "Missing POSTHOG_API_KEY. Please set it in .env or provide it."}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            if command == "list_projects":
                return self._list_projects(headers)
            elif command == "list_feature_flags":
                project_id = kwargs.get("project_id")
                if not project_id:
                     return {"success": False, "error": "project_id is required for list_feature_flags"}
                return self._list_feature_flags(headers, project_id)
            elif command == "get_insight":
                project_id = kwargs.get("project_id")
                insight_id = kwargs.get("insight_id") # Short ID or numeric ID
                if not project_id or not insight_id:
                     return {"success": False, "error": "project_id and insight_id are required"}
                return self._get_insight(headers, project_id, insight_id)
            elif command == "create_annotation":
                 project_id = kwargs.get("project_id")
                 content = kwargs.get("content")
                 date_marker = kwargs.get("date_marker") # ISO string
                 if not project_id or not content:
                      return {"success": False, "error": "project_id and content are required"}
                 return self._create_annotation(headers, project_id, content, date_marker)
            else:
                return {"success": False, "error": f"Unknown command: {command}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _list_projects(self, headers: Dict) -> Dict:
        """List all organizations and projects the user has access to."""
        # This endpoint mimics fetching 'projects' via organizations
        resp = requests.get(f"{self.base_url}/api/organizations/", headers=headers)
        resp.raise_for_status()
        data = resp.json()
        
        # Simplify output
        projects = []
        for org in data.get("results", []):
            for project in org.get("teams", []): # 'teams' are projects in PostHog schema
                projects.append({
                    "id": project["id"],
                    "name": project["name"],
                    "organization": org["name"]
                })
        return {"success": True, "projects": projects}

    def _list_feature_flags(self, headers: Dict, project_id: str) -> Dict:
        resp = requests.get(f"{self.base_url}/api/projects/{project_id}/feature_flags", headers=headers)
        resp.raise_for_status()
        # Return summary
        flags = resp.json().get("results", [])
        summary = [{"key": f["key"], "active": f["active"], "name": f.get("name")} for f in flags]
        return {"success": True, "flags": summary}

    def _get_insight(self, headers: Dict, project_id: str, insight_id: str) -> Dict:
        resp = requests.get(f"{self.base_url}/api/projects/{project_id}/insights/{insight_id}", headers=headers)
        resp.raise_for_status()
        result = resp.json()
        # insights can be complex, return key result data
        return {"success": True, "result": result.get("result"), "filters": result.get("filters")}

    def _create_annotation(self, headers: Dict, project_id: str, content: str, date_marker: Optional[str] = None) -> Dict:
        payload = {"content": content}
        if date_marker:
            payload["date_marker"] = date_marker
            
        resp = requests.post(f"{self.base_url}/api/projects/{project_id}/annotations/", headers=headers, json=payload)
        resp.raise_for_status()
        return {"success": True, "annotation": resp.json()}

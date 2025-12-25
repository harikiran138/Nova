
import docker
import requests
from typing import Dict, List, Any
from .base import BaseTool

class DockerHubTool(BaseTool):
    """Tool for interacting with Docker Hub and managing images."""
    

    @property
    def name(self) -> str:
        return "docker"

    @property
    def description(self) -> str:
        return "Manage Docker images, containers, and Compose stacks.\nMethods:\n- search(query): Find images\n- pull(image): Download image\n- list(): List images\n- inspect(image): Image details\n- compose_up(file): Start compose stack\n- compose_down(file): Stop compose stack"

    def __init__(self):
        # BaseTool doesn't have an init to call with args usually, or if it does, it's empty
        self.usage_syntax = '{"tool": "docker.compose_up", "args": {"file": "compose.yaml"}}'
        try:
            self.client = docker.from_env()
        except:
            self.client = None

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Satisfy BaseTool interface."""
        method = args.get("method", "list")
        clean_args = {k: v for k, v in args.items() if k != "method"}
        return self.run_action(method, clean_args)

    def run_action(self, method: str, args: Dict) -> Dict[str, Any]:
        if not self.client:
            return {"success": False, "error": "Docker daemon is not running. Install Docker Desktop."}

        if method == "search":
            return self._search_hub(args.get("query", ""))
        elif method == "pull":
            return self._pull_image(args.get("image", ""))
        elif method == "list":
            return self._list_images()
        elif method == "inspect":
            return self._inspect_image(args.get("image", ""))
        elif method == "compose_up":
            return self._compose_up(args.get("file", "compose.yaml"))
        elif method == "compose_down":
            return self._compose_down(args.get("file", "compose.yaml"))
        else:
            return {"success": False, "error": f"Unknown method: {method}"}

    def _compose_up(self, file_path: str) -> Dict[str, Any]:
        import subprocess
        try:
            cmd = ["docker", "compose", "-f", file_path, "up", "-d"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return {"success": True, "result": f"Stack started: {result.stdout}"}
            else:
                return {"success": False, "error": f"Compose failed: {result.stderr}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _compose_down(self, file_path: str) -> Dict[str, Any]:
        import subprocess
        try:
            cmd = ["docker", "compose", "-f", file_path, "down"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return {"success": True, "result": "Stack stopped."}
            else:
                return {"success": False, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _search_hub(self, query: str) -> Dict[str, Any]:
        """Search Docker Hub using public API."""
        if not query:
            return {"success": False, "error": "Query required"}
        
        try:
            # Docker Python SDK search is deprecated/limited, using HTTP API for better results
            url = f"https://hub.docker.com/v2/search/repositories/?query={query}&page_size=10"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                results = response.json().get("results", [])
                formatted = []
                for r in results:
                    formatted.append(f"- {r['repo_name']} (Stars: {r['star_count']}, Pulls: {r['pull_count']})")
                return {"success": True, "result": "\n".join(formatted) if formatted else "No results found."}
            else:
                return {"success": False, "error": f"Hub API Error: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _pull_image(self, image: str) -> Dict[str, Any]:
        if not image:
            return {"success": False, "error": "Image name required"}
        try:
            # This can be slow, might timeout standard tool execution, but let's try
            self.client.images.pull(image)
            return {"success": True, "result": f"Successfully pulled {image}"}
        except Exception as e:
            return {"success": False, "error": f"Pull failed: {e}"}

    def _list_images(self) -> Dict[str, Any]:
        try:
            images = self.client.images.list()
            formatted = []
            for img in images:
                tags = img.tags
                if tags:
                    formatted.append(f"- {tags[0]} ({img.short_id})")
            return {"success": True, "result": "\n".join(formatted) if formatted else "No images found."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _inspect_image(self, image: str) -> Dict[str, Any]:
        try:
            img = self.client.images.get(image)
            return {"success": True, "result": str(img.attrs)}
        except Exception as e:
            return {"success": False, "error": f"Image not found: {e}"}

import subprocess
import os
import shutil
from pathlib import Path
from typing import Dict, Any, List

class GitHubToolPuller:
    """
    Autonomous tool puller that clones GitHub repositories and looks for
    ADK-compliant tools to register.
    """
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir
        self.tools_dir = workspace_dir / ".nova" / "external_tools"
        self.tools_dir.mkdir(parents=True, exist_ok=True)

    def pull_and_register(self, repo_url: str) -> Dict[str, Any]:
        """
        Clones a repo and attempts to register tools found within.
        """
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        dest_path = self.tools_dir / repo_name
        
        try:
            if dest_path.exists():
                shutil.rmtree(dest_path)
            
            subprocess.run(["git", "clone", repo_url, str(dest_path)], check=True, capture_output=True)
            
            # Look for .py files that might be tools
            tools_found = []
            for root, _, files in os.walk(dest_path):
                for file in files:
                    if file.endswith(".py") and not file.startswith("__"):
                        tools_found.append(os.path.join(root, file))
            
            return {
                "success": True,
                "repo": repo_name,
                "tools_found": len(tools_found),
                "path": str(dest_path)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_installed_tools(self) -> List[str]:
        """List directories in the external tools folder."""
        if not self.tools_dir.exists():
            return []
        return [d.name for d in self.tools_dir.iterdir() if d.is_dir()]

import subprocess
from pathlib import Path
from typing import Dict, Any
from .base import BaseTool

class SearchCodeTool(BaseTool):
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "search.code"

    @property
    def description(self) -> str:
        return "search.code(query, path='.') - Search for code using grep"

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        query = args.get("query", "")
        path = args.get("path", ".")
        
        if not query:
            return {"success": False, "error": "Missing query"}
            
        try:
            # Use git grep if in a git repo, otherwise grep -r
            # For simplicity, we'll use grep -r
            cmd = ["grep", "-r", "-n", query, path]
            
            result = subprocess.run(
                cmd, 
                cwd=self.workspace_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode > 1: # 0=found, 1=not found, >1=error
                return {"success": False, "error": result.stderr}
                
            output = result.stdout
            if not output:
                return {"success": True, "result": "No matches found."}
                
            # Truncate if too long
            lines = output.splitlines()
            if len(lines) > 50:
                output = "\n".join(lines[:50]) + f"\n... ({len(lines)-50} more matches)"
                
            return {"success": True, "result": output}
        except Exception as e:
            return {"success": False, "error": str(e)}

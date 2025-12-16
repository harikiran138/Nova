import subprocess
from pathlib import Path
from typing import Dict, Any
from .base import BaseTool

class GitBaseTool(BaseTool):
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir
        
    def _run_git(self, args: list) -> Dict[str, Any]:
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.workspace_dir,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                return {"success": False, "error": result.stderr}
            return {"success": True, "result": result.stdout.strip()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": False, "error": "Base tool cannot be executed"}

class GitAddTool(GitBaseTool):
    @property
    def name(self) -> str: return "git.add"
    @property
    def description(self) -> str: return "git.add(files) - Add files to staging area"
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        files = args.get("files", ".")
        return self._run_git(["add", files])

class GitStatusTool(GitBaseTool):
    @property
    def name(self) -> str: return "git.status"
    @property
    def description(self) -> str: return "git.status() - Get status (auto-inits)"
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        if not (self.workspace_dir / ".git").exists():
            self._run_git(["init"])
            return {"success": True, "result": "Initialized empty Git repository."}
        return self._run_git(["status"])

class GitDiffTool(GitBaseTool):
    @property
    def name(self) -> str: return "git.diff"
    @property
    def description(self) -> str: return "git.diff(staged=False) - Show changes"
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        cmd = ["diff"]
        if args.get("staged"): cmd.append("--staged")
        return self._run_git(cmd)

class GitCommitTool(GitBaseTool):
    @property
    def name(self) -> str: return "git.commit"
    @property
    def description(self) -> str: return "git.commit(message) - Commit changes"
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        msg = args.get("message")
        if not msg: return {"success": False, "error": "Missing message"}
        return self._run_git(["commit", "-m", msg])

class GitLogTool(GitBaseTool):
    @property
    def name(self) -> str: return "git.log"
    @property
    def description(self) -> str: return "git.log(max_count=5) - Show commit logs"
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        count = str(args.get("max_count", 5))
        return self._run_git(["log", f"-n{count}", "--oneline"])

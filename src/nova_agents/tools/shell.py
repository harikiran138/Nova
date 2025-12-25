import subprocess
import re
from pathlib import Path
from typing import Dict, Any, List
from .base import BaseTool

class ShellRunTool(BaseTool):
    def __init__(self, workspace_dir: Path, allow_shell: bool, allowlist: List[str]):
        self.workspace_dir = workspace_dir
        self.allow_shell = allow_shell
        self.allowlist = allowlist

    @property
    def name(self) -> str:
        return "shell.run"

    @property
    def description(self) -> str:
        allowed = ", ".join(self.allowlist[:10])
        return f"shell.run(command) - Execute shell commands (allowed: {allowed}...)"

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        if not self.allow_shell:
            return {"success": False, "error": "Shell command execution is disabled"}
        
        command = args.get("command", "")
        if not command:
            return {"success": False, "error": "Missing required argument: command"}
        
        base_cmd = command.strip().split()[0] if command.strip() else ""
        if base_cmd not in self.allowlist:
            return {
                "success": False,
                "error": f"Command '{base_cmd}' not in allowlist. Allowed: {', '.join(self.allowlist)}"
            }
        
        dangerous_patterns = [
            r'\brm\s+-rf\b',
            r'\bformat\b',
            r'\bdd\b.*if=/dev/',
            r'\bmkfs\b',
            r'>\s*/dev/(?!null)',
            r'\bshred\b',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return {
                    "success": False,
                    "error": f"Command contains potentially destructive pattern: {pattern}"
                }
        
        # Check for nested tool calls (hallucination prevention)
        if '{"tool":' in command or "{'tool':" in command:
             return {
                "success": False,
                "error": "Invalid usage: Do not nest tool calls inside shell.run. Call the tool directly."
            }        
        # Get timeout from args or use default (120s)
        timeout = args.get("timeout", 120)
        try:
            timeout = int(timeout)
        except ValueError:
            timeout = 120

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.workspace_dir),
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\n[stderr]: {result.stderr}"
            
            return {
                "success": result.returncode == 0,
                "result": output,
                "exit_code": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Command timed out ({timeout}s limit)"}
        except Exception as e:
            return {"success": False, "error": f"Error executing command: {str(e)}"}

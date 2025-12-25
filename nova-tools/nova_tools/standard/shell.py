import subprocess
from pydantic import BaseModel, Field
from nova_core.tools.base import BaseTool
from nova_core.config import config

class ShellRunArgs(BaseModel):
    command: str = Field(..., description="Shell command to execute")

class ShellRunTool(BaseTool):
    name = "shell_run"
    description = "Execute a shell command (safe subset only)."
    args_schema = ShellRunArgs
    
    def run(self, command: str) -> str:
        if not config.allow_shell_commands:
            return "Error: Shell commands are disabled."
            
        base_cmd = command.split()[0]
        if base_cmd not in config.shell_allowlist:
            return f"Error: Command '{base_cmd}' is not allowed."
            
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=config.workspace_dir,
                timeout=30
            )
            output = result.stdout
            if result.stderr:
                output += f"\nStderr: {result.stderr}"
            return output
        except Exception as e:
            return f"Error executing command: {e}"

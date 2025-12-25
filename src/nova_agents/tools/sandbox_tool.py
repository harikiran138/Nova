from typing import Dict, Any
from src.nova_ops.docker_sandbox import DockerSandbox

class CodeSandboxTool:
    """Tool for safely executing code in a sandbox."""
    
    def __init__(self):
        self.sandbox = DockerSandbox()
        self.description = "sandbox.run_code(code, language='python') - Safely execute code in an isolated environment. Returns stdout/stderr."
        
        # Determine if actually available
        self.is_available = self.sandbox.client is not None
        if not self.is_available:
            self.description += " (CURRENTLY UNAVAILABLE: Docker not found)"

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        if not self.is_available:
            return {"success": False, "error": "Docker not available. Cannot run sandbox."}
            
        code = args.get("code", "")
        language = args.get("language", "python")
        
        if language.lower() not in ["python", "bash", "sh"]:
             return {"success": False, "error": f"Unsupported language: {language}"}

        if not code.strip():
            return {"success": False, "error": "No code provided."}

        self.sandbox.start()
        
        try:
            # Simple execution for now: write to file and run
            if language == "python":
                cmd_str = f"python3 -c '{code}'"
            else:
                cmd_str = f"bash -c '{code}'"
                
            result = self.sandbox.run_command(cmd_str)
            return {
                "success": result["success"],
                "result": result.get("output", "") or result.get("error", ""),
                "exit_code": result.get("exit_code")
            }
        finally:
            self.sandbox.stop()

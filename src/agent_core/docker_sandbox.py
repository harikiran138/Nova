import docker
from typing import Dict, Any

class DockerSandbox:
    """Runs commands in a Docker container."""
    
    def __init__(self, image: str = "python:3.9-slim"):
        self.image = image
        self.client = None
        self.container = None
        try:
            self.client = docker.from_env()
        except Exception:
            print("Docker not available.")

    def start(self):
        if not self.client: return
        try:
            self.container = self.client.containers.run(
                self.image, 
                command="tail -f /dev/null", 
                detach=True,
                auto_remove=True
            )
        except Exception as e:
            print(f"Failed to start sandbox: {e}")

    def run_command(self, cmd: str) -> Dict[str, Any]:
        if not self.container:
            return {"success": False, "error": "Sandbox not running"}
        
        try:
            exit_code, output = self.container.exec_run(cmd)
            return {
                "success": exit_code == 0,
                "output": output.decode("utf-8"),
                "exit_code": exit_code
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def stop(self):
        if self.container:
            self.container.stop()

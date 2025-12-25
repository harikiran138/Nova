import subprocess
import sys
import platform
from pathlib import Path
from typing import Dict, Any
from .base import BaseTool

class SystemInstallerTool(BaseTool):
    """Tool for installing system packages and Python libraries."""
    
    @property
    def name(self) -> str:
        return "system_install"

    @property
    def description(self) -> str:
        return "system_install(package, manager='pip') - Install packages via pip, brew, or apt."

    def execute(self, **kwargs) -> Dict[str, Any]:
        package = kwargs.get("package")
        manager = kwargs.get("manager", "pip").lower()
        
        if not package:
            return {"success": False, "error": "Package name required."}

        # Safety check is handled by SafetyPolicy in AgentLoop, 
        # but we can add a sanity check here.
        if ";" in package or "&&" in package:
             return {"success": False, "error": "Invalid package name (potential injection)."}

        try:
            if manager == "pip":
                cmd = [sys.executable, "-m", "pip", "install", package]
            elif manager == "brew":
                if platform.system() != "Darwin":
                    return {"success": False, "error": "Homebrew is only for macOS."}
                cmd = ["brew", "install", package]
            elif manager == "apt":
                if platform.system() == "Darwin":
                    return {"success": False, "error": "apt is not available on macOS."}
                cmd = ["sudo", "apt-get", "install", "-y", package]
            else:
                return {"success": False, "error": f"Unsupported package manager: {manager}"}

            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            # Secure Auto-Installation: Log version and lock dependencies
            if manager == "pip" and result.returncode == 0:
                try:
                    # Get version
                    show_cmd = [sys.executable, "-m", "pip", "show", package]
                    show_res = subprocess.run(show_cmd, capture_output=True, text=True)
                    version = "unknown"
                    for line in show_res.stdout.splitlines():
                        if line.startswith("Version:"):
                            version = line.split(":", 1)[1].strip()
                            break
                    
                    # Update requirements.txt if it exists in CWD
                    req_path = Path.cwd() / "requirements.txt"
                    if req_path.exists():
                        with open(req_path, "a") as f:
                            f.write(f"\n{package}=={version}")
                            
                    # Log to audit (simulated print for now, real audit log is elsewhere)
                    # console.print(f"[dim]Locked {package}=={version} in requirements.txt[/dim]")
                    
                except Exception as e:
                    pass # Don't fail the tool if logging fails

            return {"success": True, "result": result.stdout}

        except subprocess.CalledProcessError as e:
            return {"success": False, "error": f"Installation failed: {e.stderr}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

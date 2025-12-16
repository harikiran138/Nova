import os
import shutil
import subprocess
import platform
import psutil
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional

class BaseTool:
    """Base class for all tools."""
    name: str = "base"
    description: str = "Base tool"
    
    def execute(self, **kwargs) -> Any:
        raise NotImplementedError

class FileTool:
    """File system operations."""
    
    def __init__(self, workspace: Path, sandbox_mode: bool = False):
        self.workspace = workspace
        self.sandbox_mode = sandbox_mode

    def _safe_path(self, path: str) -> Path:
        """Ensure path is within workspace if sandbox is active."""
        target = (self.workspace / path).resolve()
        if self.sandbox_mode:
            try:
                target.relative_to(self.workspace.resolve())
            except ValueError:
                raise PermissionError(f"Access denied: {path} is outside workspace.")
        return target

    def read(self, path: str) -> str:
        return self._safe_path(path).read_text()

    def write(self, path: str, content: str):
        p = self._safe_path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)

    def list(self, path: str = ".") -> List[str]:
        p = self._safe_path(path)
        return [str(f.relative_to(self.workspace)) for f in p.glob("*")]

    def mkdir(self, path: str):
        self._safe_path(path).mkdir(parents=True, exist_ok=True)

    def move(self, src: str, dst: str):
        shutil.move(str(self._safe_path(src)), str(self._safe_path(dst)))

    def copy(self, src: str, dst: str):
        shutil.copy2(str(self._safe_path(src)), str(self._safe_path(dst)))

    def delete(self, path: str) -> str:
        """Delete a file or directory."""
        target_path = self._safe_path(path)
        try:
            if target_path.is_dir():
                shutil.rmtree(target_path)
            else:
                target_path.unlink()
            return f"Deleted {path}"
        except Exception as e:
            return f"Error deleting {path}: {e}"

class GitTool:
    """Git operations."""
    
    def __init__(self, workspace: Path):
        self.workspace = workspace

    def _run(self, args: List[str]) -> str:
        return subprocess.check_output(
            ["git"] + args, cwd=self.workspace, text=True, stderr=subprocess.STDOUT
        )

    def status(self) -> str:
        return self._run(["status"])

    def diff(self) -> str:
        return self._run(["diff"])

    def log(self, n: int = 5) -> str:
        return self._run(["log", f"-n {n}", "--oneline"])

    def commit(self, message: str):
        return self._run(["commit", "-m", message])

    def add(self, files: List[str]):
        return self._run(["add"] + files)

class ShellTool:
    """Safe shell execution."""
    def __init__(self, workspace: Path):
        self.workspace = workspace

    def run(self, command: str, cwd: str = None) -> str:
        """Run a shell command."""
        work_dir = (self.workspace / cwd).resolve() if cwd else self.workspace
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=work_dir, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            return result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return "Error: Command timed out."
        except Exception as e:
            return f"Error: {e}"

    def run_safe(self, command: str) -> str:
        """Alias for run (safety handled by policy)."""
        return self.run(command)

    def list_processes(self) -> str:
        """List running processes."""
        return "\n".join([f"{p.pid}: {p.name()}" for p in psutil.process_iter(['pid', 'name'])])

    def kill_safe(self, pid: int) -> str:
        """Kill a process by PID."""
        try:
            p = psutil.Process(pid)
            p.terminate()
            return f"Process {pid} terminated."
        except Exception as e:
            return f"Error killing process {pid}: {e}"

class NetTool:
    """Tools for network access."""
    
    def __init__(self, offline_mode: bool = True):
        self.offline_mode = offline_mode
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })

    def _check_permission(self) -> str:
        """Check if network access is allowed."""
        if self.offline_mode:
            return "PERMISSION_DENIED: This requires external data. Should I connect to the internet? (yes/no)"
        return None

    def get(self, url: str) -> str:
        """Get content from a URL."""
        denied = self._check_permission()
        if denied: return denied
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            # Limit content size
            return response.text[:500000]
        except Exception as e:
            return f"Error fetching {url}: {e}"

    def post(self, url: str, data: str) -> str:
        """Post data to a URL."""
        denied = self._check_permission()
        if denied: return denied
        
        try:
            response = self.session.post(url, json=json.loads(data), timeout=10)
            response.raise_for_status()
            return response.text[:50000]
        except Exception as e:
            return f"Error posting to {url}: {e}"
            
    def download_file(self, url: str, filepath: str) -> str:
        """Download a file from a URL."""
        denied = self._check_permission()
        if denied: return denied
        
        try:
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return f"Successfully downloaded {url} to {filepath}"
        except Exception as e:
            return f"Error downloading {url}: {e}"

    def search(self, query: str) -> str:
        """Search the web (mocked for now, but would use an API)."""
        denied = self._check_permission()
        if denied: return denied
        
        # In a real implementation, this would call a search API
        # For now, we'll just return a placeholder or use a public search if available
        return f"Search results for '{query}' (Mock): [Result 1]..."
        
    def check_connection(self, host: str = "8.8.8.8", port: int = 53, timeout: int = 3) -> str:
        """Check internet connectivity."""
        denied = self._check_permission()
        if denied: return denied
        
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return "Online"
        except Exception as e:
            return f"Offline: {e}"

class SysTool:
    """System information."""
    
    def usage(self) -> Dict[str, Any]:
        return {
            "cpu": psutil.cpu_percent(),
            "ram": psutil.virtual_memory().percent
        }

    def osinfo(self) -> Dict[str, str]:
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version()
        }

    def env(self) -> Dict[str, str]:
        return dict(os.environ)

    def disk_usage(self, path: str = "/") -> Dict[str, Any]:
        """Get disk usage."""
        du = shutil.disk_usage(path)
        return {"total": du.total, "used": du.used, "free": du.free}

    def network_info(self) -> Dict[str, Any]:
        """Get network interface info."""
        return {k: v[0].address for k, v in psutil.net_if_addrs().items()}

    def open_file(self, path: str) -> str:
        """Open a file with default application (macOS/Linux)."""
        cmd = "open" if platform.system() == "Darwin" else "xdg-open"
        subprocess.run([cmd, path])
        return f"Opened {path}"

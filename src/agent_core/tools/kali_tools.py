try:
    import docker
except ImportError:
    docker = None

from pathlib import Path
from typing import Dict, Any

class KaliTool:
    """Interface to Kali Linux tools via Docker."""
    
    IMAGE = "kalilinux/kali-rolling"
    
    SESSION_NAME = "nova-kali-session"

    def __init__(self, workspace: Path):
        self.workspace = workspace.resolve()
        self.client = None
        self.session_active = False
        if docker:
            try:
                self.client = docker.from_env()
                # Check if session already exists
                try:
                    self.client.containers.get(self.SESSION_NAME)
                    self.session_active = True
                except docker.errors.NotFound:
                    self.session_active = False
            except Exception:
                print("Warning: Docker not available. Kali tools disabled.")
        else:
            print("Warning: 'docker' module not installed.")

    def _ensure_image(self):
        if not self.client: return False
        try:
            self.client.images.get(self.IMAGE)
            return True
        except docker.errors.ImageNotFound:
            print(f"Pulling {self.IMAGE}...")
            self.client.images.pull(self.IMAGE)
            return True
        except Exception as e:
            print(f"Docker Error: {e}")
            return False

    def start_session(self) -> str:
        """Start a persistent Kali session."""
        if not self.client: return "Docker not available."
        if self.session_active: return "Session already active."
        
        try:
            self._ensure_image()
            self.client.containers.run(
                self.IMAGE,
                command="tail -f /dev/null", # Keep alive
                name=self.SESSION_NAME,
                volumes={str(self.workspace): {'bind': '/workspace', 'mode': 'rw'}},
                working_dir="/workspace",
                detach=True,
                network_mode="host",
                auto_remove=True
            )
            self.session_active = True
            return "Kali session started."
        except Exception as e:
            return f"Failed to start session: {e}"

    def stop_session(self) -> str:
        """Stop the persistent session."""
        if not self.client: return "Docker not available."
        try:
            container = self.client.containers.get(self.SESSION_NAME)
            container.stop()
            self.session_active = False
            return "Kali session stopped."
        except Exception as e:
            return f"Failed to stop session: {e}"

    def run(self, command: str) -> str:
        """Run a command in the Kali container (session or ephemeral)."""
        if not self.client: return "Error: Docker/Kali not available."
        
        try:
            if self.session_active:
                # Run in existing session
                container = self.client.containers.get(self.SESSION_NAME)
                exit_code, output = container.exec_run(
                    f"bash -c '{command}'",
                    workdir="/workspace"
                )
                out_str = output.decode("utf-8")
                if exit_code == 127: # Command not found
                     return self._handle_missing_tool(command)
                return out_str
            else:
                # Run ephemeral
                self._ensure_image()
                output = self.client.containers.run(
                    self.IMAGE,
                    command=f"bash -c '{command}'",
                    volumes={str(self.workspace): {'bind': '/workspace', 'mode': 'rw'}},
                    working_dir="/workspace",
                    remove=True,
                    network_mode="host"
                )
                return output.decode("utf-8")
        except docker.errors.ContainerError as e:
            if e.exit_status == 127:
                return self._handle_missing_tool(command)
            return f"Kali Execution Error: {e}"
        except Exception as e:
            return f"Kali Execution Error: {e}"

    def _handle_missing_tool(self, command: str) -> str:
        cmd_name = command.split()[0]
        return f"Error: Tool '{cmd_name}' not found. Run `kali.start_session()` then `kali.install('{cmd_name}')`."

    def install(self, packages: str) -> str:
        """Install packages (requires active session)."""
        if not self.session_active:
            return "Error: Must start a session first. Run `kali.start_session()`."
        return self.run(f"apt-get update && apt-get install -y {packages}")

    # Convenience wrappers for common tools
    def nmap(self, target: str, args: str = "") -> str:
        return self.run(f"nmap {args} {target}")
        
    def sqlmap(self, url: str, args: str = "") -> str:
        return self.run(f"sqlmap -u {url} {args} --batch")
        
    def nikto(self, host: str) -> str:
        return self.run(f"nikto -h {host}")
        
    def metasploit(self, command: str) -> str:
        return self.run(f"msfconsole -x '{command}; exit'")

    def dnsmasq(self, args: str = "") -> str:
        """Run dnsmasq."""
        return self.run(f"dnsmasq {args}")

    def ettercap(self, args: str = "") -> str:
        """Run ettercap."""
        return self.run(f"ettercap {args}")

    def faraday(self, args: str = "") -> str:
        """Run faraday."""
        return self.run(f"faraday {args}")

    def hashcat(self, args: str = "") -> str:
        """Run hashcat."""
        return self.run(f"hashcat {args}")

    def maltego(self, args: str = "") -> str:
        """Run maltego."""
        return self.run(f"maltego {args}")

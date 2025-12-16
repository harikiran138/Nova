from typing import Dict, Any, List, Callable, Optional
from pathlib import Path
from .core_tools import FileTool, GitTool, NetTool, SysTool, ShellTool
from .kali_tools import KaliTool
from .memory_tool import MemoryTool
from .api_tool import ApiTool
from .docker_tools import DockerHubTool
from .installer import SystemInstallerTool
from ..memory import MemoryManager
from ..plugins import PluginManager

class ToolWrapper:
    """Wraps a tool function with metadata."""
    def __init__(self, name: str, func: Callable, description: str = None):
        self.name = name
        self.func = func
        self.description = description or func.__doc__ or "No description available."
        
    def __call__(self, **kwargs):
        return self.func(**kwargs)

class ToolRegistry:
    """Registry for agent tools."""
    
    def __init__(self, workspace_dir: Path, allow_shell: bool = False, shell_allowlist: List[str] = None, offline_mode: bool = True):
        self.workspace_dir = workspace_dir
        self.allow_shell = allow_shell
        self.shell_allowlist = shell_allowlist or []
        self.offline_mode = offline_mode
        self.tools: Dict[str, ToolWrapper] = {}
        
        # Initialize Memory
        self.memory_manager = MemoryManager(workspace_dir / ".nova" / "memory")
        
        # Initialize Tool Sets
        self.file_tools_instance = FileTool(workspace_dir)
        self.git_tools_instance = GitTool(workspace_dir)
        self.net_tools_instance = NetTool(offline_mode=self.offline_mode)
        self.sys_tools_instance = SysTool()
        self.shell_tools_instance = ShellTool(workspace_dir)
        self.kali_tools_instance = KaliTool(workspace_dir)
        self.mem_tools_instance = MemoryTool(self.memory_manager)
        self.api_tools_instance = ApiTool()
        self.installer_tools_instance = SystemInstallerTool()
        self.docker_tools_instance = DockerHubTool()
        
        from .web_tools import WebSearchTool
        self.web_search_tool_instance = WebSearchTool()
        
        # Backward compatibility attributes (deprecated)
        self.file = self.file_tools_instance
        self.git = self.git_tools_instance
        self.net = self.net_tools_instance
        self.sys = self.sys_tools_instance
        self.shell = self.shell_tools_instance
        self.kali = self.kali_tools_instance
        self.mem = self.mem_tools_instance
        self.api = self.api_tools_instance
        
        self._register_defaults()
        self._register_kali_tools()
        self.register("memory.remember", self.mem.remember, "Remember a fact for future sessions.")
        self.register("memory.recall", self.mem.recall, "Recall learned facts.")
        self.register("memory.recall", self.mem.recall, "Recall learned facts.")
        self.register("api.request", self.api.request, "Make HTTP API requests (JSON/REST).")
        self.register("system.install", self.installer_tools_instance.execute, "Install packages (pip, brew, apt).")

        # Docker Tools
        self.register("docker.search", lambda **k: self.docker_tools_instance.run_action("search", k), "Search Docker Hub")
        self.register("docker.pull", lambda **k: self.docker_tools_instance.run_action("pull", k), "Pull Docker image")
        self.register("docker.list", lambda **k: self.docker_tools_instance.run_action("list", k), "List Docker images")
        self.register("docker.compose_up", lambda **k: self.docker_tools_instance.run_action("compose_up", k), "Start Docker Compose stack")
        self.register("docker.compose_down", lambda **k: self.docker_tools_instance.run_action("compose_down", k), "Stop Docker Compose stack")

        
        self._load_plugins()

    def _register_defaults(self):
        """Register default core tools."""
        # File Tools
        self.register("file.read", self.file_tools_instance.read, "Read file content")
        self.register("file.write", self.file_tools_instance.write, "Write content to file")
        self.register("file.list", self.file_tools_instance.list, "List directory contents")
        self.register("file.mkdir", self.file_tools_instance.mkdir, "Create directory")
        self.register("file.move", self.file_tools_instance.move, "Move a file or directory")
        self.register("file.copy", self.file_tools_instance.copy, "Copy a file or directory")
        self.register("file.delete", self.file_tools_instance.delete, "Delete a file or directory")
        
        # Git Tools
        self.register("git.status", self.git_tools_instance.status)
        self.register("git.diff", self.git_tools_instance.diff)
        self.register("git.log", self.git_tools_instance.log)
        self.register("git.commit", self.git_tools_instance.commit)
        self.register("git.add", self.git_tools_instance.add)
        
        # Network Tools
        self.register("net.get", self.net_tools_instance.get, "GET request to URL")
        self.register("net.post", self.net_tools_instance.post, "POST request to URL")
        self.register("net.download", self.net_tools_instance.download_file, "Download file from URL")
        self.register("net.check", self.net_tools_instance.check_connection, "Check internet connection")
        # self.register("net.search", self.net_tools_instance.search, "Search the web") 
        self.register("web.search", self.web_search_tool_instance.execute, "Search the web using DuckDuckGo")
        self.register("net.search", self.web_search_tool_instance.execute, "Alias for web.search")
        
        # System Tools
        self.register("sys.netinfo", self.sys.network_info)
        self.register("sys.open", self.sys.open_file)

        # Shell Tools
        self.register("shell.run", self.shell.run)
        self.register("shell.run_safe", self.shell.run_safe)
        self.register("shell.list", self.shell.list_processes)
        self.register("shell.kill", self.shell.kill_safe)

    def _register_kali_tools(self):
        # Kali Security Tools
        self.register("kali.start_session", self.kali.start_session)
        self.register("kali.stop_session", self.kali.stop_session)
        self.register("kali.run", self.kali.run)
        self.register("kali.install", self.kali.install)
        self.register("kali.nmap", self.kali.nmap)
        self.register("kali.sqlmap", self.kali.sqlmap)
        self.register("kali.nikto", self.kali.nikto)
        self.register("kali.msf", self.kali.metasploit)
        self.register("kali.dnsmasq", self.kali.dnsmasq)
        self.register("kali.ettercap", self.kali.ettercap)
        self.register("kali.faraday", self.kali.faraday)
        self.register("kali.hashcat", self.kali.hashcat)
        self.register("kali.maltego", self.kali.maltego)

    def _load_plugins(self):
        """Load plugins from the plugins directory."""
        self.plugin_manager = PluginManager(Path.home() / ".nova" / "plugins")
        self.plugin_manager.load_plugins(self)

    def register(self, name: str, func: Callable, description: str = None):
        self.tools[name] = ToolWrapper(name, func, description)

    def get_tool(self, name: str) -> ToolWrapper:
        return self.tools.get(name)

    def execute(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """Execute a tool safely."""
        tool = self.get_tool(tool_name)
        if not tool:
            return {"success": False, "error": f"Tool '{tool_name}' not found."}
            
        try:
            # Call with unpacked arguments
            result = tool(**args)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": f"Error executing {tool_name}: {e}"}

    @property
    def tool_definitions(self) -> List[Dict[str, Any]]:
        """Generate JSON schema for LLM."""
        import inspect
        schemas = []
        for name, tool in self.tools.items():
            sig = inspect.signature(tool.func)
            params = {}
            required = []
            
            for param_name, param in sig.parameters.items():
                if param_name == "self": continue
                
                param_type = "string"
                if param.annotation == int: param_type = "integer"
                elif param.annotation == bool: param_type = "boolean"
                elif param.annotation == dict: param_type = "object"
                elif param.annotation == list: param_type = "array"
                
                params[param_name] = {
                    "type": param_type,
                    "description": f"Argument {param_name}" 
                }
                if param.default == inspect.Parameter.empty:
                    required.append(param_name)
            
            schemas.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object", 
                        "properties": params,
                        "required": required
                    } 
                }
            })
        return schemas

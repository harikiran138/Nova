from pathlib import Path
from typing import List, Dict, Any, Optional
from src.agent_core.tools.core_tools import FileTool, ShellTool, NetTool

class ToolRegistry:
    """Simple registry that maps tool names to implementations.
    Exposes execute() and net_tools_instance used by tests.
    """
    def __init__(self, workspace_dir: Path = None, allow_shell: bool = False, shell_allowlist: List[str] = None, sandbox_mode: bool = True, offline_mode: bool = True):
        self.workspace_dir = Path(workspace_dir or ".").resolve()
        self.file_tools = FileTool(self.workspace_dir, sandbox_mode=sandbox_mode)
        self.shell_tool = ShellTool(self.workspace_dir, allow_shell=allow_shell, allowlist=shell_allowlist or [])
        self.net_tools_instance = NetTool(offline_mode=offline_mode)
        # Register mapping
        self._tools = {
            "file.read": self._file_read,
            "file.write": self._file_write,
            "file.list": self._file_list,
            "file.mkdir": self._file_mkdir,
            "file.makedirs": self._file_mkdirs,
            "shell.run": self._shell_run,
            "net.get": self._net_get,
        }

    def register(self, name: str, func):
        self._tools[name] = func

    def list(self) -> List[str]:
        return list(self._tools.keys())

    def execute(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        handler = self._tools.get(name)
        if not handler:
            return {"success": False, "error": f"Unknown tool: {name}"}
        try:
            return handler(args)
        except PermissionError as e:
            return {"success": False, "error": f"Access denied: {e}"}
        except ValueError as e:
            return {"success": False, "error": f"{e}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # Handlers
    def _file_read(self, args: Dict[str, Any]) -> Dict[str, Any]:
        path = args.get("path", "")
        if not path:
            return {"success": False, "error": "Missing required argument: path"}
        content = self.file_tools.read(path)
        return {"success": True, "result": content}

    def _file_write(self, args: Dict[str, Any]) -> Dict[str, Any]:
        path = args.get("path", "")
        content = args.get("content", "")
        if not path:
            return {"success": False, "error": "Missing required argument: path"}
        self.file_tools.write(path, content)
        return {"success": True, "result": f"File written successfully: {path}"}

    def _file_list(self, args: Dict[str, Any]) -> Dict[str, Any]:
        path = args.get("path", ".")
        items = self.file_tools.list(path)
        # Prepend file type indicators to mimic expected format
        lines = []
        for item in items:
            p = (self.workspace_dir / item).resolve()
            type_char = "d" if p.is_dir() else "f"
            lines.append(f"{type_char} {Path(item).name}")
        return {"success": True, "result": "\n".join(sorted(lines))}

    def _file_mkdir(self, args: Dict[str, Any]) -> Dict[str, Any]:
        path = args.get("path", "")
        if not path:
            return {"success": False, "error": "Missing required argument: path"}
        self.file_tools.mkdir(path)
        return {"success": True, "result": f"Directory created: {path}"}

    def _file_mkdirs(self, args: Dict[str, Any]) -> Dict[str, Any]:
        path = args.get("path", "")
        if not path:
            return {"success": False, "error": "Missing required argument: path"}
        self.file_tools.mkdir(path)  # mkdir with parents True already
        return {"success": True, "result": f"Directory created (including parents): {path}"}

    def _shell_run(self, args: Dict[str, Any]) -> Dict[str, Any]:
        command = args.get("command", "")
        if not command:
            return {"success": False, "error": "Missing required argument: command"}
        # Prevent nested tool calls in shell
        if '{"tool":' in command or "{'tool':" in command:
            return {"success": False, "error": "Invalid usage: Do not nest tool calls inside shell.run. Call the tool directly."}
        output = self.shell_tool.run(command)
        # If command was disallowed, ShellTool raises ValueError which is caught
        return {"success": True, "result": output, "exit_code": 0}

    def _net_get(self, args: Dict[str, Any]) -> Dict[str, Any]:
        url = args.get("url", "")
        if not url:
            return {"success": False, "error": "Missing required argument: url"}
        result = self.net_tools_instance.get(url)
        if isinstance(result, str) and result.startswith("PERMISSION_DENIED"):
            return {"success": False, "error": result}
        return {"success": True, "result": result}

__all__ = ["ToolRegistry"]

from pathlib import Path
from typing import Dict, Any
from .base import BaseTool

class FileReadTool(BaseTool):
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "file.read"

    @property
    def description(self) -> str:
        return "file.read(path) - Read a file from the workspace"

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        path_str = args.get("path", "")
        if not path_str:
            return {"success": False, "error": "Missing required argument: path"}
        
        try:
            file_path = (self.workspace_dir / path_str).resolve()
            if not str(file_path).startswith(str(self.workspace_dir)):
                return {"success": False, "error": "Path must be within workspace directory"}
            
            if not file_path.exists():
                return {"success": False, "error": f"File not found: {path_str}"}
            
            if not file_path.is_file():
                return {"success": False, "error": f"Not a file: {path_str}"}
            
            content = file_path.read_text(encoding="utf-8")
            return {"success": True, "result": content}
        except Exception as e:
            return {"success": False, "error": f"Error reading file: {str(e)}"}

class FileWriteTool(BaseTool):
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "file.write"

    @property
    def description(self) -> str:
        return "file.write(path, content) - Write content to a file in the workspace"

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        path_str = args.get("path", "")
        content = args.get("content", "")
        
        if not path_str:
            return {"success": False, "error": "Missing required argument: path"}
        
        try:
            file_path = (self.workspace_dir / path_str).resolve()
            if not str(file_path).startswith(str(self.workspace_dir)):
                return {"success": False, "error": "Path must be within workspace directory"}
            
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
            return {"success": True, "result": f"File written successfully: {path_str}"}
        except Exception as e:
            return {"success": False, "error": f"Error writing file: {str(e)}"}

class FileListTool(BaseTool):
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "file.list"

    @property
    def description(self) -> str:
        return "file.list(path) - List files in a directory (default: root)"

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        path_str = args.get("path", ".")
        
        try:
            dir_path = (self.workspace_dir / path_str).resolve()
            if not str(dir_path).startswith(str(self.workspace_dir)):
                return {"success": False, "error": "Path must be within workspace directory"}
            
            if not dir_path.exists():
                return {"success": False, "error": f"Directory not found: {path_str}"}
            
            if not dir_path.is_dir():
                return {"success": False, "error": f"Not a directory: {path_str}"}
            
            items = []
            for item in dir_path.iterdir():
                type_char = "d" if item.is_dir() else "f"
                items.append(f"{type_char} {item.name}")
            
            return {"success": True, "result": "\n".join(sorted(items))}
        except Exception as e:
            return {"success": False, "error": f"Error listing directory: {str(e)}"}

class FilePatchTool(BaseTool):
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "file.patch"

    @property
    def description(self) -> str:
        return "file.patch(path, target_content, replacement_content) - Replace a text block in a file"

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        path_str = args.get("path", "")
        target = args.get("target_content", "")
        replacement = args.get("replacement_content", "")
        
        if not path_str or not target:
            return {"success": False, "error": "Missing path or target_content"}
            
        try:
            file_path = (self.workspace_dir / path_str).resolve()
            if not file_path.exists():
                return {"success": False, "error": f"File not found: {path_str}"}
                
            content = file_path.read_text(encoding="utf-8")
            
            if target not in content:
                # Try fuzzy match or ignore whitespace? For now strict.
                return {"success": False, "error": "Target content not found in file"}
                
            # Replace only the first occurrence for safety, or all?
            # Usually patch implies specific location.
            # Let's replace one occurrence.
            new_content = content.replace(target, replacement, 1)
            
            file_path.write_text(new_content, encoding="utf-8")
            return {"success": True, "result": f"Successfully patched {path_str}"}
        except Exception as e:
            return {"success": False, "error": f"Error patching file: {str(e)}"}

class FileMkdirTool(BaseTool):
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "file.mkdir"

    @property
    def description(self) -> str:
        return "file.mkdir(path) - Create a directory (fails if parent missing)"

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        path_str = args.get("path", "")
        if not path_str:
            return {"success": False, "error": "Missing required argument: path"}
            
        try:
            dir_path = (self.workspace_dir / path_str).resolve()
            if not str(dir_path).startswith(str(self.workspace_dir)):
                return {"success": False, "error": "Path must be within workspace directory"}
            
            if dir_path.exists() and dir_path.is_file():
                return {"success": False, "error": f"Cannot create directory '{path_str}': A file with this name already exists."}
            
            dir_path.mkdir(parents=False, exist_ok=True)
            return {"success": True, "result": f"Directory created: {path_str}"}
        except FileNotFoundError:
             return {"success": False, "error": f"Parent directory missing for: {path_str}. Use file.makedirs for nested paths."}
        except Exception as e:
            return {"success": False, "error": f"Error creating directory: {str(e)}"}

class FileMakedirsTool(BaseTool):
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "file.makedirs"

    @property
    def description(self) -> str:
        return "file.makedirs(path) - Create a directory and any missing parents"

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        path_str = args.get("path", "")
        if not path_str:
            return {"success": False, "error": "Missing required argument: path"}
            
        try:
            dir_path = (self.workspace_dir / path_str).resolve()
            if not str(dir_path).startswith(str(self.workspace_dir)):
                return {"success": False, "error": "Path must be within workspace directory"}
            
            dir_path.mkdir(parents=True, exist_ok=True)
            return {"success": True, "result": f"Directory created (including parents): {path_str}"}
        except Exception as e:
            return {"success": False, "error": f"Error creating directory: {str(e)}"}

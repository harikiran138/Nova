from typing import Optional
from pydantic import BaseModel, Field
from pathlib import Path
from nova_core.tools.base import BaseTool
from nova_core.config import config

class FileReadArgs(BaseModel):
    path: str = Field(..., description="Path to the file to read")

class FileReadTool(BaseTool):
    name = "file_read"
    description = "Read the contents of a file from the workspace."
    args_schema = FileReadArgs
    
    def run(self, path: str) -> str:
        target_path = (config.workspace_dir / path).resolve()
        if not str(target_path).startswith(str(config.workspace_dir.resolve())):
            return "Error: Path must be within workspace."
        if not target_path.exists():
            return "Error: File not found."
        return target_path.read_text()

class FileWriteArgs(BaseModel):
    path: str = Field(..., description="Path to the file to write")
    content: str = Field(..., description="Content to write to the file")

class FileWriteTool(BaseTool):
    name = "file_write"
    description = "Write content to a file in the workspace."
    args_schema = FileWriteArgs
    
    def run(self, path: str, content: str) -> str:
        target_path = (config.workspace_dir / path).resolve()
        if not str(target_path).startswith(str(config.workspace_dir.resolve())):
            return "Error: Path must be within workspace."
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(content)
        return f"Successfully wrote to {path}"

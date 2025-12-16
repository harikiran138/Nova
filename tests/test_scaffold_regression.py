import pytest
from pathlib import Path
from src.agent_core.tools.file import FileMkdirTool, FileMakedirsTool
from src.agent_core.tools.shell import ShellRunTool

def test_file_mkdir(tmp_path):
    tool = FileMkdirTool(tmp_path)
    
    # Test creating a directory
    result = tool.execute({"path": "test_dir"})
    assert result["success"] is True
    assert (tmp_path / "test_dir").exists()
    
    # Test creating existing directory (should succeed)
    result = tool.execute({"path": "test_dir"})
    assert result["success"] is True
    
    # Test missing parent (should fail)
    result = tool.execute({"path": "missing_parent/child"})
    assert result["success"] is False
    assert "Parent directory missing" in result["error"]

def test_file_makedirs(tmp_path):
    tool = FileMakedirsTool(tmp_path)
    
    # Test creating nested directories
    result = tool.execute({"path": "nested/dirs/here"})
    assert result["success"] is True
    assert (tmp_path / "nested/dirs/here").exists()

def test_shell_run_rejects_nested_json(tmp_path):
    tool = ShellRunTool(tmp_path, allow_shell=True, allowlist=["ls", "echo"])
    
    # Test nested tool call
    result = tool.execute({"command": 'echo {"tool": "file.write"}'})
    assert result["success"] is False
    assert "Invalid usage" in result["error"]
    
    # Test valid command
    result = tool.execute({"command": "echo hello"})
    assert result["success"] is True

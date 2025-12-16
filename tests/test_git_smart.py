import pytest
import subprocess
from pathlib import Path
from src.agent_core.tools.git import GitStatusTool, GitAddTool

@pytest.fixture
def temp_git_repo(tmp_path):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    return repo_dir

def test_git_status_auto_init(temp_git_repo):
    tool = GitStatusTool(temp_git_repo)
    
    # Should auto-init
    result = tool.execute({})
    assert result["success"] is True
    assert "Initialized empty Git repository" in result["result"]
    assert (temp_git_repo / ".git").exists()
    
    # Subsequent call should be normal status
    result = tool.execute({})
    assert result["success"] is True
    assert "On branch" in result["result"]

def test_git_add(temp_git_repo):
    # Init first
    GitStatusTool(temp_git_repo).execute({})
    
    # Create a file
    (temp_git_repo / "test.txt").write_text("content")
    
    # Add file
    add_tool = GitAddTool(temp_git_repo)
    result = add_tool.execute({"files": "test.txt"})
    assert result["success"] is True
    
    # Check status to confirm added
    status_tool = GitStatusTool(temp_git_repo)
    result = status_tool.execute({})
    assert "Changes to be committed" in result["result"]
    assert "new file:   test.txt" in result["result"]

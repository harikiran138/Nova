import pytest
from src.agent_core.error_analysis import analyze_error, COMMON_ERRORS

def test_analyze_error_missing_package():
    """Test analysis of missing package error."""
    error_msg = "ModuleNotFoundError: No module named 'requests'"
    result = analyze_error(error_msg)
    
    assert result is not None
    assert result["type"] == "missing_package"
    assert result["target"] == "requests"
    assert result["action"] == "install_package"

def test_analyze_error_command_not_found():
    """Test analysis of command not found error."""
    error_msg = "command not found: docker"
    result = analyze_error(error_msg)
    
    assert result is not None
    assert result["type"] == "missing_command"
    assert result["target"] == "docker"
    assert result["action"] == "install_system_tool"

def test_analyze_error_type_error():
    """Test analysis of common type error."""
    error_msg = 'TypeError: can only concatenate str (not "int") to str'
    result = analyze_error(error_msg)
    
    assert result is not None
    assert result["type"] == "code_error"
    assert "Ensure both operands are strings" in result["fix"]

def test_analyze_error_unknown_error():
    """Test analysis of an unknown error."""
    error_msg = "SomeRandomError: This is totally unexpected"
    result = analyze_error(error_msg)
    
    assert result is None

def test_analyze_error_git_error():
    """Test analysis of git error."""
    error_msg = "fatal: not a git repository"
    result = analyze_error(error_msg)
    
    assert result is not None
    assert result["type"] == "git_error"
    assert "Run 'git init'" in result["fix"]

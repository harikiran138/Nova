"""
Static knowledge base for common runtime errors and their fixes.
Used by the AgentLoop for Root Cause Intelligence before searching the web.
"""

import re

COMMON_ERRORS = {
    r"ModuleNotFoundError: No module named '(\w+)'": {
        "type": "missing_package",
        "action": "install_package",
        "description": "Missing Python package."
    },
    r"ImportError: No module named (\w+)": {
        "type": "missing_package",
        "action": "install_package",
        "description": "Missing Python package."
    },
    r"command not found: (\w+)": {
        "type": "missing_command",
        "action": "install_system_tool",
        "description": "Missing system command."
    },
    r"TypeError: can only concatenate str \(not \"int\"\) to str": {
        "type": "code_error",
        "action": "suggest_fix",
        "fix": "Ensure both operands are strings. Use str(variable) to convert integers.",
        "description": "Type mismatch in string concatenation."
    },
    r"NameError: name '(\w+)' is not defined": {
        "type": "code_error",
        "action": "suggest_fix",
        "fix": "Define the variable before using it, or check for typos.",
        "description": "Undefined variable."
    },
    r"IndentationError": {
        "type": "code_error",
        "action": "suggest_fix",
        "fix": "Check code indentation. Ensure consistent use of spaces or tabs.",
        "description": "Indentation error."
    },
    r"fatal: not a git repository": {
        "type": "git_error",
        "action": "suggest_fix",
        "fix": "Run 'git init' to initialize a repository.",
        "description": "Not a git repository."
    },
    r"fatal: remote origin already exists": {
        "type": "git_error",
        "action": "suggest_fix",
        "fix": "Use 'git remote set-url origin <url>' to update the URL.",
        "description": "Remote origin exists."
    },
    r"Docker is not running": {
        "type": "docker_error",
        "action": "suggest_fix",
        "fix": "Start the Docker daemon (Docker Desktop or systemctl start docker).",
        "description": "Docker daemon not running."
    },
    r"ConnectionRefusedError": {
        "type": "network_error",
        "action": "suggest_fix",
        "fix": "Check if the target service is running and listening on the correct port.",
        "description": "Connection refused."
    }
}

def analyze_error(error_msg: str):
    """Analyze an error message and return a known fix if available."""
    for pattern, info in COMMON_ERRORS.items():
        match = re.search(pattern, error_msg)
        if match:
            result = info.copy()
            if match.groups():
                result["target"] = match.group(1)
            return result
    return None

import time
import json
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple, Union

class SafetyLevel(Enum):
    READ_ONLY = "read_only"         # No file writes, no shell
    SANDBOX_ONLY = "sandbox_only"   # Writes/Shell only in sandbox
    RESTRICTED = "restricted"       # Dangerous tools require confirmation
    UNRESTRICTED = "unrestricted"   # Full access (use with caution)

class AuditLogger:
    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, action: str, details: dict, allowed: bool, reason: str):
        entry = {
            "timestamp": time.time(),
            "action": action,
            "details": details,
            "allowed": allowed,
            "reason": reason
        }
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

class TokenManager:
    """Manages temporary permission tokens for high-risk actions."""
    def __init__(self):
        self.tokens = {}

    def generate_token(self, action: str, duration: int = 300) -> str:
        import secrets
        token = secrets.token_hex(16)
        self.tokens[token] = {
            "action": action,
            "expires": time.time() + duration
        }
        return token

    def validate_token(self, token: str, action: str) -> bool:
        if token not in self.tokens: return False
        data = self.tokens[token]
        if time.time() > data["expires"]:
            del self.tokens[token]
            return False
        if data["action"] != action: return False
        return True

class SafetyPolicy:
    DANGEROUS_COMMANDS = ["rm", "kill", "chmod", "chown", "dd", "mkfs", "reboot", "shutdown", "wget", "curl"]
    
    def __init__(self, level: SafetyLevel, workspace_dir: Path, sandbox_dir: Optional[Path] = None, security_mode: bool = False):
        self.level = level
        self.workspace_dir = workspace_dir
        self.sandbox_dir = sandbox_dir or (Path.home() / ".nova" / "sandbox")
        self.audit = AuditLogger(Path.home() / ".nova" / "audit.log")
        self.security_mode = security_mode
        self.token_manager = TokenManager()

    def check_tool_permission(self, tool_name: str, args: dict, token: str = None) -> Tuple[bool, str]:
        """
        Check if a tool execution is allowed.
        Returns: (Allowed, Reason/ConfirmationMessage)
        """
        reason = "Allowed by policy"
        allowed = True
        
        # 0. Zero-Trust Validation (Token Check for High Risk)
        if tool_name in ["file.delete", "system.install"] or (tool_name == "shell.run" and self._is_dangerous(args.get("command", ""))):
            if token and self.token_manager.validate_token(token, tool_name):
                return True, "Authorized by Permission Token"
            elif self.security_mode:
                return False, "Action denied: High-risk action requires Permission Token in Security Mode."

        # 1. SECURITY MODE Check (Highest Priority)
        if self.security_mode:
            # Block irreversible actions (unless tokenized above)
            if tool_name in ["file.delete", "system.install"]:
                return False, "Action denied in Security-First Mode (Irreversible)."
            
            # Block network/cloud/pentest tools
            if tool_name.startswith("kali.") or tool_name.startswith("net.") or tool_name.startswith("web."):
                return False, "Action denied in Security-First Mode (Network/Cloud)."
                
            # Enforce Sandbox for ALL file operations
            if tool_name.startswith("file."):
                path = args.get("path")
                if path:
                    full_path = (self.workspace_dir / path).resolve()
                    if not self._is_in_sandbox(full_path):
                        return False, f"Access denied: {path} is outside sandbox (Security Mode)."
        
        # 2. READ_ONLY Check
        if self.level == SafetyLevel.READ_ONLY:
            if tool_name in ["file.write", "file.patch", "shell.run", "shell.run_safe", "git.commit", "shell.kill_safe"]:
                return False, "Action denied in READ_ONLY mode."

        # 3. SANDBOX Check
        if self.level == SafetyLevel.SANDBOX_ONLY:
            if tool_name in ["file.write", "file.patch"]:
                path = args.get("path")
                if path:
                    full_path = (self.workspace_dir / path).resolve()
                    if not self._is_in_sandbox(full_path):
                        return False, f"Access denied: {path} is outside sandbox."
            
            if tool_name in ["shell.run", "shell.run_safe"]:
                # For shell, we rely on the tool to use the sandbox CWD, 
                # but we should block dangerous commands even in sandbox if they escape.
                cmd = args.get("command", "")
                if self._is_dangerous(cmd):
                     return False, "Dangerous command denied in SANDBOX_ONLY mode."

        # 4. RESTRICTED Check (Confirmation)
        if self.level == SafetyLevel.RESTRICTED or self.level == SafetyLevel.SANDBOX_ONLY:
             if tool_name in ["shell.run", "shell.run_safe", "shell.kill_safe"]:
                 cmd = args.get("command", "")
                 if self._is_dangerous(cmd) or tool_name == "shell.kill_safe":
                     return False, "CONFIRM_REQUIRED" # Special signal for AgentLoop

        self.audit.log(tool_name, args, allowed, reason)
        return allowed, reason

    def _is_in_sandbox(self, path: Path) -> bool:
        try:
            return str(path).startswith(str(self.sandbox_dir.resolve()))
        except:
            return False

    def _is_dangerous(self, cmd: str) -> bool:
        """Heuristic check for dangerous commands."""
        parts = cmd.split()
        if not parts: return False
        base_cmd = parts[0]
        # Check exact match or if it's in a chain (&&, |)
        if base_cmd in self.DANGEROUS_COMMANDS: return True
        if any(f" {d} " in f" {cmd} " for d in self.DANGEROUS_COMMANDS): return True
        return False

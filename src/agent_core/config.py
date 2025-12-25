"""Configuration management for Nova Agent CLI."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class Config:
    """Configuration for Nova Agent CLI.
    
    Attributes:
        ollama_base_url: Base URL for Ollama API
        ollama_model: Model name to use (e.g., 'llama3')
        workspace_dir: Directory for file operations
        allow_shell_commands: Whether to allow shell command execution
        shell_command_allowlist: List of allowed shell command base names
    """
    ollama_base_url: str
    ollama_model: str
    ollama_embedding_model: str
    model_provider: str # 'ollama'
    mongodb_uri: str
    mongodb_db_name: str
    mongodb_collection_name: str
    workspace_dir: Path
    allow_shell_commands: bool
    shell_command_allowlist: List[str]
    shell_command_allowlist: List[str]
    offline_mode: bool = True # Default to offline
    enable_autonomous_install: bool = False
    enable_auto_model_switch: bool = False
    security_mode: bool = False
    turbo_mode: bool = False
    safety_level: str = "unrestricted"
    safety_level: str = "unrestricted"
    use_mongodb: bool = False
    use_docker: bool = False
    temperature: float = 0.7

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables and .env file."""
        # Search paths for .env
        search_paths = [
            Path.cwd() / ".env",
            Path.home() / ".env",
            Path.home() / ".nova" / ".env",
            Path(__file__).parent.parent.parent / ".env" # Project root if running from source
        ]
        
        for env_path in search_paths:
            if env_path.exists():
                # console.print(f"[dim]Loading config from {env_path}[/dim]") # Debug
                with open(env_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            # Only set if not already in env (env vars take precedence)
                            if key not in os.environ:
                                os.environ[key] = value

        # Force disable ChromaDB telemetry
        os.environ["ANONYMIZED_TELEMETRY"] = "False"

        # Get workspace directory
        workspace_str = os.getenv("WORKSPACE_DIR")
        if workspace_str:
            workspace_dir = Path(workspace_str).resolve()
        else:
            workspace_dir = Path.cwd()
            
        workspace_dir.mkdir(parents=True, exist_ok=True)
        
        # Parse shell command allowlist
        allowlist_str = os.getenv(
            "SHELL_COMMAND_ALLOWLIST",
            "ls,cat,echo,pwd,python,python3,node,npm,git,curl,wget,head,tail,grep,find,mkdir,rm,cp,mv,touch"
        )
        allowlist = [cmd.strip() for cmd in allowlist_str.split(",") if cmd.strip()]
        
        # Parse allow shell commands flag
        allow_shell = os.getenv("ALLOW_SHELL_COMMANDS", "true").lower() == "true"
        
        # Parse offline mode flag
        offline_mode = os.getenv("NOVA_OFFLINE_MODE", "true").lower() == "true"
        
        # Parse autonomous flags
        enable_autonomous_install = os.getenv("ENABLE_AUTONOMOUS_INSTALL", "false").lower() == "true"
        enable_auto_model_switch = os.getenv("ENABLE_AUTO_MODEL_SWITCH", "false").lower() == "true"
        security_mode = os.getenv("SECURITY_MODE", "false").lower() == "true"
        turbo_mode = os.getenv("TURBO_MODE", "false").lower() == "true"
        safety_level = os.getenv("SAFETY_LEVEL", "unrestricted").lower()

        return cls(
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
            ollama_model=os.getenv("OLLAMA_MODEL", "mannix/llama3.1-8b-abliterated"),
            ollama_embedding_model=os.getenv("OLLAMA_EMBEDDING_MODEL", "all-minilm"),
            model_provider=os.getenv("MODEL_PROVIDER", "ollama"),
            workspace_dir=workspace_dir,
            allow_shell_commands=allow_shell,
            shell_command_allowlist=allowlist,
            offline_mode=offline_mode,
            enable_autonomous_install=enable_autonomous_install,
            enable_auto_model_switch=enable_auto_model_switch,
            security_mode=security_mode,
            turbo_mode=turbo_mode,
            safety_level=safety_level,
            mongodb_uri=os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
            mongodb_db_name=os.getenv("MONGODB_DB_NAME", "nova_agent_db"),
            mongodb_collection_name=os.getenv("MONGODB_COLLECTION_NAME", "knowledge_base"),
            use_mongodb=os.getenv("USE_MONGODB", "false").lower() == "true",
            use_docker=os.getenv("USE_DOCKER", "false").lower() == "true",
            temperature=float(os.getenv("TEMPERATURE", "0.7"))
        )
    
    def load_profiles(self) -> dict:
        """Load agent profiles from profiles.yaml."""
        import yaml
        
        profile_path = Path(__file__).parent / "profiles.yaml"
        if not profile_path.exists():
            return {}
            
        try:
            with open(profile_path, "r") as f:
                data = yaml.safe_load(f)
                return data.get("profiles", {})
        except Exception as e:
            print(f"Error loading profiles: {e}")
            return {}

    def load_user_profile(self) -> dict:
        """Load user profile from user_profile.yaml."""
        import yaml
        
        profile_path = Path(__file__).parent / "user_profile.yaml"
        if not profile_path.exists():
            return {}
            
        try:
            with open(profile_path, "r") as f:
                data = yaml.safe_load(f)
                return data.get("user", {})
        except Exception as e:
            print(f"Error loading user profile: {e}")
            return {}

    
    @staticmethod
    def update_env_variable(key: str, value: str):
        """Update or add an environment variable in the .env file."""
        env_path = Path.cwd() / ".env"
        
        # Read existing lines
        lines = []
        if env_path.exists():
            with open(env_path, "r") as f:
                lines = f.readlines()
        
        # Process lines
        key_found = False
        new_lines = []
        for line in lines:
            if line.strip().startswith(f"{key}="):
                new_lines.append(f"{key}={value}\n")
                key_found = True
            else:
                new_lines.append(line)
        
        # Append if not found
        if not key_found:
            # Ensure proper spacing
            if new_lines and not new_lines[-1].endswith("\n"):
                new_lines[-1] += "\n"
            new_lines.append(f"{key}={value}\n")
            
        # Write back
        with open(env_path, "w") as f:
            f.writelines(new_lines)
            
        # Update current process env as well
        os.environ[key] = value

    def validate(self) -> List[str]:
        """Validate configuration and return any error messages.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Validate Ollama URL
        if not self.ollama_base_url.startswith(("http://", "https://")):
            errors.append(f"Invalid OLLAMA_BASE_URL: {self.ollama_base_url}")
        
        # Validate workspace directory
        if not self.workspace_dir.exists():
            errors.append(f"Workspace directory does not exist: {self.workspace_dir}")
        
        return errors

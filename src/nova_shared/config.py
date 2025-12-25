"""Configuration management for Nova Agent CLI."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any


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
    gemini_model: str
    ollama_embedding_model: str
    model_provider: str # 'ollama' or 'gemini'
    mongodb_uri: str
    mongodb_db_name: str
    mongodb_collection_name: str
    workspace_dir: Path
    allow_shell_commands: bool
    shell_command_allowlist: List[str]
    offline_mode: bool = True # Default to offline
    enable_autonomous_install: bool = False
    enable_auto_model_switch: bool = False
    security_mode: bool = False
    turbo_mode: bool = False
    safety_level: str = "unrestricted"
    use_mongodb: bool = False
    use_docker: bool = False
    max_tokens: int = 512
    temperature: float = 0.3
    gemini_api_key: str = ""
    typing_speed: float = 0.005
    skip_animations: bool = False
    circuit_breaker_threshold: int = 5
    model_options: Dict[str, Any] = None

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables and .env file."""
        # Search paths for .env
        search_paths = [
            Path.cwd() / ".env",
            Path.home() / ".nova" / ".env",
        ]
        
        for env_path in search_paths:
            if env_path.exists():
                # console.print(f"[dim]Loading config from {env_path}[/dim]") # Debug
                with open(env_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            key, value = line.split("=", 1)
                            os.environ[key] = value

        workspace_dir = Path(os.getenv("WORKSPACE_DIR", str(Path.cwd())))
        allow_shell = os.getenv("ALLOW_SHELL_COMMANDS", "true").lower() == "true"
        allowlist = os.getenv("SHELL_COMMAND_ALLOWLIST", "ls,cat,grep,find,git").split(",")
        offline_mode = os.getenv("OFFLINE_MODE", "true").lower() == "true"
        enable_autonomous_install = os.getenv("ENABLE_AUTONOMOUS_INSTALL", "false").lower() == "true"
        enable_auto_model_switch = os.getenv("ENABLE_AUTO_MODEL_SWITCH", "false").lower() == "true"
        security_mode = os.getenv("SECURITY_MODE", "false").lower() == "true"
        turbo_mode = os.getenv("TURBO_MODE", "false").lower() == "true"
        skip_animations = os.getenv("NOVA_SKIP_ANIMATIONS", "false").lower() == "true"
        safety_level = os.getenv("SAFETY_LEVEL", "unrestricted").lower()

        return cls(
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
            ollama_model=os.getenv("OLLAMA_MODEL", "mannix/llama3.1-8b-abliterated"),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
            ollama_embedding_model=os.getenv("OLLAMA_EMBEDDING_MODEL", "all-minilm"),
            model_provider=os.getenv("MODEL_PROVIDER", "ollama"),
            mongodb_uri=os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
            mongodb_db_name=os.getenv("MONGODB_DB_NAME", "nova_agent_db"),
            mongodb_collection_name=os.getenv("MONGODB_COLLECTION_NAME", "knowledge_base"),
            workspace_dir=workspace_dir,
            allow_shell_commands=allow_shell,
            shell_command_allowlist=allowlist,
            offline_mode=offline_mode,
            enable_autonomous_install=enable_autonomous_install,
            enable_auto_model_switch=enable_auto_model_switch,
            security_mode=security_mode,
            turbo_mode=turbo_mode,
            safety_level=safety_level,
            use_mongodb=os.getenv("USE_MONGODB", "false").lower() == "true",
            use_docker=os.getenv("USE_DOCKER", "false").lower() == "true",
            max_tokens=int(os.getenv("MAX_TOKENS", "512")),
            temperature=float(os.getenv("TEMPERATURE", "0.3")),
            gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
            typing_speed=float(os.getenv("TYPING_SPEED", "0.005")),
            skip_animations=skip_animations,
            circuit_breaker_threshold=int(os.getenv("CIRCUIT_BREAKER_THRESHOLD", "5")),
            model_options={}
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
                return data if data else {}
        except Exception as e:
            print(f"Error loading user profile: {e}")
            return {}

    def validate(self) -> List[str]:
        """Validate the configuration and return list of errors."""
        errors = []
        if not self.ollama_base_url.startswith("http"):
            errors.append(f"Invalid OLLAMA_BASE_URL: {self.ollama_base_url}")
        return errors

    def update_env(self, key: str, value: str):
        """Update environment variable and persist to .nova/.env."""
        os.environ[key] = value
        env_path = Path.home() / ".nova" / ".env"
        env_path.parent.mkdir(parents=True, exist_ok=True)
        
        lines = []
        if env_path.exists():
            with open(env_path, "r") as f:
                lines = f.readlines()
        
        found = False
        new_lines = []
        for line in lines:
            if line.startswith(f"{key}="):
                new_lines.append(f"{key}={value}\n")
                found = True
            else:
                new_lines.append(line)
        
        if not found:
            new_lines.append(f"{key}={value}\n")
            
        with open(env_path, "w") as f:
            f.writelines(new_lines)

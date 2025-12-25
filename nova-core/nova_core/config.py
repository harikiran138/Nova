from pydantic import BaseModel, Field
from typing import List, Optional
import os
from pathlib import Path

class NovaConfig(BaseModel):
    """Central configuration for Nova v2."""
    
    # Ollama Settings
    ollama_base_url: str = Field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"))
    ollama_model: str = Field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "llama3"))
    
    # Paths
    workspace_dir: Path = Field(default_factory=lambda: Path(os.getenv("WORKSPACE_DIR", "./workspace")))
    database_path: Path = Field(default_factory=lambda: Path(os.getenv("DATABASE_PATH", "./nova.db")))
    
    # Safety
    allow_shell_commands: bool = Field(default_factory=lambda: os.getenv("ALLOW_SHELL_COMMANDS", "true").lower() == "true")
    shell_allowlist: List[str] = Field(
        default_factory=lambda: os.getenv("SHELL_COMMAND_ALLOWLIST", "ls,cat,echo,pwd,git,grep,find,python,python3,node,npm").split(",")
    )
    
    class Config:
        env_file = ".env"

# Global config instance
config = NovaConfig()

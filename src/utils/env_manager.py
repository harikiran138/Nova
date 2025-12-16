import os
from pathlib import Path
from typing import Dict

class EnvManager:
    """Helper to safely update .env files."""
    
    def __init__(self, env_path: Path):
        self.env_path = env_path

    def update(self, updates: Dict[str, str]):
        """Update specific keys in the .env file."""
        if not self.env_path.exists():
            return

        with open(self.env_path, "r") as f:
            lines = f.readlines()

        new_lines = []
        updated_keys = set()

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                new_lines.append(line)
                continue

            try:
                key, value = line.split("=", 1)
                key = key.strip()
                if key in updates:
                    new_lines.append(f"{key}={updates[key]}")
                    updated_keys.add(key)
                else:
                    new_lines.append(line)
            except ValueError:
                new_lines.append(line)

        # Append new keys that weren't in the file
        for key, value in updates.items():
            if key not in updated_keys:
                new_lines.append(f"{key}={value}")

        with open(self.env_path, "w") as f:
            f.write("\n".join(new_lines) + "\n")

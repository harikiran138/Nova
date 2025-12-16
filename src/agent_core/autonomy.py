import subprocess
from pathlib import Path
from rich.console import Console

console = Console()

class ErrorPredictor:
    """Predicts potential errors before execution."""
    
    ANTI_PATTERNS = [
        ("rm -rf /", "High Risk: Root directory deletion"),
        ("chmod 777", "Security Risk: Permissive permissions"),
        ("while True", "Potential Infinite Loop"),
        ("eval(", "Security Risk: Code Injection"),
    ]

    def check_risk(self, code_or_command: str) -> str:
        for pattern, warning in self.ANTI_PATTERNS:
            if pattern in code_or_command:
                return warning
        return None

class RollbackManager:
    """Manages git-based rollbacks for safe autonomy."""
    
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir

    def create_checkpoint(self, name: str):
        """Create a git tag/commit as a checkpoint."""
        try:
            subprocess.run(["git", "add", "."], cwd=self.workspace_dir, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", f"Checkpoint: {name}"], cwd=self.workspace_dir, check=False, capture_output=True)
            subprocess.run(["git", "tag", "-f", f"checkpoint_{name}"], cwd=self.workspace_dir, check=True, capture_output=True)
            console.print(f"[dim]Checkpoint '{name}' created.[/dim]")
        except Exception as e:
            console.print(f"[red]Failed to create checkpoint: {e}[/red]")

    def rollback(self, name: str):
        """Revert to a checkpoint."""
        try:
            subprocess.run(["git", "checkout", "-f", f"checkpoint_{name}"], cwd=self.workspace_dir, check=True, capture_output=True)
            console.print(f"[yellow]Rolled back to checkpoint '{name}'.[/yellow]")
        except Exception as e:
            console.print(f"[red]Rollback failed: {e}[/red]")

class IntentModel:
    """Predicts user intent based on history."""
    
    def __init__(self):
        self.patterns = {
            "git add": "git commit",
            "git commit": "git push",
            "pip install": "pip freeze > requirements.txt",
            "mkdir": "cd",
            "test": "fix",
        }

    def predict_next(self, last_action: str) -> str:
        for key, value in self.patterns.items():
            if key in last_action:
                return value
        return None

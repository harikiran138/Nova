import shutil
import os
from pathlib import Path
from rich.console import Console

console = Console()

class Sandbox:
    """Manages the Nova sandbox environment."""
    
    DEFAULT_PATH = Path.home() / ".nova" / "sandbox"
    
    def __init__(self, path: Path = None):
        self.path = path if path else self.DEFAULT_PATH
        
    def init(self):
        """Initialize the sandbox directory."""
        if not self.path.exists():
            self.path.mkdir(parents=True, exist_ok=True)
            console.print(f"[green]✓ Sandbox initialized at {self.path}[/green]")
        else:
            console.print(f"[yellow]Sandbox already exists at {self.path}[/yellow]")
            
    def clean(self):
        """Clean the sandbox directory."""
        if self.path.exists():
            # Safety check: ensure we are deleting the expected sandbox path
            if "sandbox" not in str(self.path):
                console.print(f"[red]Safety Error: Path {self.path} does not look like a sandbox![/red]")
                return
                
            shutil.rmtree(self.path)
            self.path.mkdir(parents=True, exist_ok=True)
            console.print(f"[green]✓ Sandbox cleaned[/green]")
        else:
            console.print("[yellow]Sandbox does not exist[/yellow]")
            
    def get_info(self):
        """Get information about the sandbox."""
        if not self.path.exists():
            return "Sandbox not initialized."
            
        file_count = sum(1 for _ in self.path.rglob('*') if _.is_file())
        size_bytes = sum(f.stat().st_size for f in self.path.rglob('*') if f.is_file())
        
        return f"""
[bold]Sandbox Information[/bold]
Path: [cyan]{self.path}[/cyan]
Files: {file_count}
Size: {size_bytes / 1024:.2f} KB
"""

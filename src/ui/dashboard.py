import time
import psutil
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.console import Console
from rich.align import Align
from rich.text import Text
from ..agent_core.config import Config

class Dashboard:
    def __init__(self):
        self.console = Console()
        self.config = Config.from_env()

    def get_system_stats(self):
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        return f"CPU: {cpu}% | RAM: {mem}%"

    def get_mode_panel(self):
        mode = "Unknown"
        color = "white"
        
        if self.config.security_mode and self.config.turbo_mode:
             mode = "Turbo (Security)"
             color = "yellow"
        elif self.config.security_mode:
            mode = "Security-First"
            color = "green"
        elif self.config.turbo_mode:
            mode = "Performance Turbo"
            color = "cyan"
        elif self.config.enable_autonomous_install and self.config.enable_auto_model_switch and not self.config.security_mode:
             if self.config.safety_level == "unrestricted":
                 mode = "Maximum Autonomy"
                 color = "magenta"
             else:
                 mode = "Balanced Intelligence"
                 color = "blue"
        
        return Panel(
            Align.center(Text(mode, style=f"bold {color}")),
            title="Operational Mode",
            border_style=color
        )

    def get_config_table(self):
        table = Table(show_header=False, box=None)
        table.add_column("Key", style="dim")
        table.add_column("Value", style="bold")
        
        table.add_row("Offline Mode", str(self.config.offline_mode))
        table.add_row("Auto-Install", str(self.config.enable_autonomous_install))
        table.add_row("Auto-Switch", str(self.config.enable_auto_model_switch))
        table.add_row("Safety Level", self.config.safety_level.upper())
        table.add_row("Model Provider", self.config.model_provider)
        
        return Panel(table, title="Configuration", border_style="blue")

    def get_telemetry_panel(self):
        from src.nova_ops.telemetry import TelemetryManager
        from src.nova_shared.config import Config
        config = Config.from_env()
        
        tm = TelemetryManager(config.workspace_dir / ".nova" / "telemetry.json")
        stats = tm.get_stats()
        
        table = Table(show_header=False, box=None)
        table.add_column("Metric", style="dim")
        table.add_column("Value", style="bold green")
        
        table.add_row("Success Rate", stats["success_rate"])
        table.add_row("Total Tasks", str(stats["total_tasks"]))
        table.add_row("Avg Duration", stats["avg_duration"])
        
        # New Metrics
        tokens = stats.get("tokens", {})
        cache = stats.get("cache", {})
        
        table.add_row("Total Tokens", str(tokens.get("total", 0)))
        table.add_row("  Prompt", str(tokens.get("prompt", 0)))
        table.add_row("  Compl.", str(tokens.get("completion", 0)))
        
        hits = cache.get("hits", 0)
        misses = cache.get("misses", 0)
        total_reqs = hits + misses
        hit_rate = f"{(hits/total_reqs*100):.1f}%" if total_reqs > 0 else "0.0%"
        
        table.add_row("Cache Hit Rate", hit_rate)
        table.add_row("  Hits", str(hits))
        
        return Panel(table, title="Agent Metrics", border_style="green")

    def get_system_panel(self):
        return Panel(
            Align.center(Text(self.get_system_stats(), style="bold white")),
            title="System Load",
            border_style="red"
        )

    def render(self):
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body")
        )
        layout["header"].update(Panel(Align.center(Text("Nova Agent Dashboard", style="bold white")), style="on blue"))
        
        layout["body"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        layout["left"].split_column(
            Layout(self.get_mode_panel()),
            Layout(self.get_system_panel())
        )
        
        layout["right"].split_column(
            Layout(self.get_config_table()),
            Layout(self.get_telemetry_panel())
        )
        
        return layout

    def run(self):
        with Live(self.render(), refresh_per_second=4) as live:
            while True:
                # Reload config to reflect changes
                self.config = Config.from_env()
                live.update(self.render())
                time.sleep(0.25)

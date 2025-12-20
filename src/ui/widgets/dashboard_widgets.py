from textual.app import ComposeResult
from textual.widgets import Static, Digits, Sparkline, Log
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
import psutil
import time

class SystemMonitor(Static):
    """Monitor CPU, RAM, and Acceleration."""
    
    cpu_usage = reactive(0.0)
    ram_usage = reactive(0.0)
    accel_type = reactive("CPU")
    
    def compose(self) -> ComposeResult:
        with Vertical(classes="panel monitor-panel"):
            yield Static("SYSTEM STATUS", classes="header-small")
            
            with Horizontal(classes="monitor-row"):
                yield Static("CPU", classes="label")
                yield Digits("", id="cpu_digits")
                
            with Horizontal(classes="monitor-row"):
                yield Static("RAM", classes="label")
                yield Digits("", id="ram_digits")
                
            yield Static("ACCELERATION", classes="label-small")
            yield Static("Checking...", id="accel_status", classes="status-text")

    def on_mount(self):
        self.set_interval(1.0, self.update_stats)

    def update_stats(self):
        self.cpu_usage = psutil.cpu_percent()
        self.ram_usage = psutil.virtual_memory().percent
        
        self.query_one("#cpu_digits", Digits).update(f"{self.cpu_usage:02.0f}%")
        self.query_one("#ram_digits", Digits).update(f"{self.ram_usage:02.0f}%")

    def watch_accel_type(self, value):
        icon = "🚀" if value != "CPU" else "🐌"
        self.query_one("#accel_status", Static).update(f"{icon} {value}")

class VisionPanel(Static):
    """Reflects what the agent 'sees'."""
    
    last_image = reactive("")
    analysis = reactive("No visual input yet.")
    
    def compose(self) -> ComposeResult:
        with Vertical(classes="panel vision-panel"):
             yield Static("VISUAL CORTEX", classes="header-small")
             yield Static("👁 Awaiting input...", id="vision_feed", classes="vision-content")
             
    def watch_last_image(self, value):
        if value:
            self.query_one("#vision_feed", Static).update(f"Analyzing: {value}...")
            
    def watch_analysis(self, value):
        self.query_one("#vision_feed", Static).update(value)

class MemoryStream(Static):
    """Live stream of agent thoughts/memories."""
    
    def compose(self) -> ComposeResult:
        with Vertical(classes="panel memory-panel"):
            yield Static("MEMORY STREAM", classes="header-small")
            yield Log(id="memory_log", classes="memory-log")
            
    def add_entry(self, text: str):
        log = self.query_one("#memory_log", Log)
        log.write_line(text)

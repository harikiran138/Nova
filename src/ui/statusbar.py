from textual.app import ComposeResult
from textual.widgets import Static
from textual.reactive import reactive
from .palette import NovaPalette

class StatusBar(Static):
    """Bottom status bar showing agent state."""
    
    model = reactive("Loading...")
    agent = reactive("General")
    tools_count = reactive(0)
    sandbox_active = reactive(False)
    workspace = reactive("Global")
    
    DEFAULT_CSS = """
    StatusBar {
        dock: bottom;
        height: 1;
        background: #151520;
        color: #808090;
        layout: horizontal;
    }
    
    .status-item {
        padding: 0 1;
    }
    
    .sandbox-safe {
        color: #00ff9d;
        text-style: bold;
    }
    
    .sandbox-unsafe {
        color: #ff0055;
        text-style: bold;
    }
    """
    
    def compose(self) -> ComposeResult:
        yield Static(f"🤖 {self.model}", id="model", classes="status-item")
        yield Static(f"👤 {self.agent}", id="agent", classes="status-item")
        yield Static(f"🛠️ {self.tools_count}", id="tools", classes="status-item")
        
        sandbox_status = "SAFE" if self.sandbox_active else "UNSAFE"
        sandbox_class = "sandbox-safe" if self.sandbox_active else "sandbox-unsafe"
        yield Static(f"🔒 {sandbox_status}", id="sandbox", classes=f"status-item {sandbox_class}")
        
        yield Static(f"📂 {self.workspace}", id="workspace", classes="status-item")

    def watch_model(self, value):
        if self.is_mounted:
            self.query_one("#model", Static).update(f"🤖 {value}")
        
    def watch_agent(self, value):
        if self.is_mounted:
            self.query_one("#agent", Static).update(f"👤 {value}")
        
    def watch_tools_count(self, value):
        if self.is_mounted:
            self.query_one("#tools", Static).update(f"🛠️ {value}")
        
    def watch_sandbox_active(self, value):
        if self.is_mounted:
            status = "SAFE" if value else "UNSAFE"
            cls = "sandbox-safe" if value else "sandbox-unsafe"
            w = self.query_one("#sandbox", Static)
            w.update(f"🔒 {status}")
            w.classes = f"status-item {cls}"
        
    def watch_workspace(self, value):
        if self.is_mounted:
            self.query_one("#workspace", Static).update(f"📂 {value}")

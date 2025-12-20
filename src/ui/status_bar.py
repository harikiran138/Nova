from textual.app import ComposeResult
from textual.widgets import Static
from textual.reactive import reactive

class StatusBar(Static):
    """Bottom status bar with rich indicators."""
    
    model = reactive("Loading...")
    agent = reactive("General")
    tools_count = reactive(0)
    sandbox_active = reactive(False)
    turbo_active = reactive(False)
    vision_active = reactive(False)
    acceleration = reactive("CPU")
    git_branch = reactive("main")
    
    # Styles moved to ThemeManager
    DEFAULT_CSS = ""
    
    def compose(self) -> ComposeResult:
        yield Static(f"🤖 {self.model}", id="model", classes="status-item")
        yield Static(f"👤 {self.agent}", id="agent", classes="status-item")
        yield Static(f"🛠️ {self.tools_count}", id="tools", classes="status-item")
        
        sandbox_status = "SAFE" if self.sandbox_active else "UNSAFE"
        sandbox_class = "sandbox-safe" if self.sandbox_active else "sandbox-unsafe"
        yield Static(f"🔒 {sandbox_status}", id="sandbox", classes=f"status-item {sandbox_class}")

        if self.turbo_active:
             yield Static("⚡ TURBO", id="turbo", classes="status-item turbo-on")
        
        if self.vision_active:
             yield Static("👁 VISION", id="vision", classes="status-item vision-on")
             
        yield Static(f"🚀 {self.acceleration}", id="accel", classes="status-item")
        
        yield Static(f"🌿 {self.git_branch}", id="git", classes="status-item")

    def watch_model(self, value):
        if self.is_mounted: self.query_one("#model", Static).update(f"🤖 {value}")
        
    def watch_agent(self, value):
        if self.is_mounted: self.query_one("#agent", Static).update(f"👤 {value}")
        
    def watch_tools_count(self, value):
        if self.is_mounted: self.query_one("#tools", Static).update(f"🛠️ {value}")
        
    def watch_turbo_active(self, value):
         # Dynamic mounting/unmounting is complex, we just toggle visibility if we rebuild structure
         # For simplicity, let's assume simple update or we'd need to re-compose
         pass

    def watch_vision_active(self, value):
         # Typically requires re-compose or we just use style.display, but for now placeholder
         pass

    def watch_acceleration(self, value):
        if self.is_mounted: self.query_one("#accel", Static).update(f"🚀 {value}")

    def watch_sandbox_active(self, value):
        if self.is_mounted:
            status = "SAFE" if value else "UNSAFE"
            cls = "sandbox-safe" if value else "sandbox-unsafe"
            w = self.query_one("#sandbox", Static)
            w.update(f"🔒 {status}")
            w.classes = f"status-item {cls}"
            
    def watch_git_branch(self, value):
        if self.is_mounted: self.query_one("#git", Static).update(f"🌿 {value}")

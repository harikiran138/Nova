from textual.app import ComposeResult
from textual.widgets import Static, RichLog, TabbedContent, TabPane
from textual.containers import Vertical, Horizontal

class ChatPanel(Vertical):
    """Main chat area."""
    
    def compose(self) -> ComposeResult:
        yield RichLog(id="chat_log", markup=True, wrap=True, highlight=True)
        
    def print(self, content: str):
        self.query_one("#chat_log", RichLog).write(content)

class ToolPanel(Vertical):
    """Side panel for tools and logs."""
    
    DEFAULT_CSS = """
    ToolPanel {
        width: 30%;
        dock: right;
        border-left: solid #3d59a1;
        background: #16161e;
    }
    """
    
    def compose(self) -> ComposeResult:
        with TabbedContent():
            with TabPane("Tools", id="tab_tools"):
                yield RichLog(id="tool_log", markup=True)
            with TabPane("Logs", id="tab_logs"):
                yield RichLog(id="debug_log", markup=True)
                
    def log_tool(self, content: str):
        self.query_one("#tool_log", RichLog).write(content)
        
    def log_debug(self, content: str):
        self.query_one("#debug_log", RichLog).write(content)

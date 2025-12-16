from textual.widgets import Static, Markdown
from textual.containers import VerticalScroll
from textual.message import Message

class ChatMessage(Static):
    """A single chat message bubble."""
    
    def __init__(self, role: str, content: str):
        super().__init__()
        self.role = role
        self.content = content
        
    def compose(self):
        role_color = "$primary" if self.role == "Nova" else "$accent"
        yield Static(f"[{role_color}]{self.role}[/{role_color}]", classes="message-header")
        yield Markdown(self.content, classes="message-content")

class ChatWindow(VerticalScroll):
    """Scrollable chat history."""
    
    DEFAULT_CSS = """
    ChatWindow {
        background: $background;
        padding: 1;
    }
    
    ChatMessage {
        margin-bottom: 1;
        padding: 1;
        background: $surface;
        border: solid $border;
    }
    
    .message-header {
        text-style: bold;
        margin-bottom: 1;
    }
    """
    
    def add_message(self, role: str, content: str):
        """Add a new message to the chat."""
        self.mount(ChatMessage(role, content))
        self.scroll_end(animate=True)
    
    def clear_chat(self):
        """Clear all messages."""
        self.remove_children()

from textual.widgets import TextArea
from textual.binding import Binding
from textual.message import Message

class InputBox(TextArea):
    """Multi-line input box for user commands."""
    
    BINDINGS = [
        Binding("enter", "submit", "Send Message"),
        Binding("ctrl+j", "voice", "Voice Input"),
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.show_line_numbers = False
        self.language = "markdown"
        
    def action_submit(self):
        """Submit the message."""
        message = self.text.strip()
        if message:
            self.post_message(self.Submitted(message))
            self.clear()
            
    class Submitted(Message):
        """Posted when user presses Enter."""
        def __init__(self, value: str):
            super().__init__()
            self.value = value

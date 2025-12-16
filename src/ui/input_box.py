from textual.widgets import TextArea
from textual.message import Message
from textual.binding import Binding

class InputBox(TextArea):
    """Multi-line input box for chat."""
    
    BINDINGS = [
        Binding("enter", "submit", "Send Message", priority=True),
        Binding("shift+enter", "newline", "New Line"),
    ]
    
    class Submitted(Message):
        def __init__(self, value: str):
            self.value = value
            super().__init__()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.show_line_numbers = False

    def action_submit(self):
        """Submit the text."""
        value = self.text.strip()
        if value:
            self.post_message(self.Submitted(value))
            self.text = ""
            
    def action_newline(self):
        """Insert newline."""
        self.insert("\n")

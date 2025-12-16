from textual.screen import ModalScreen
from textual.widgets import Input, ListView, ListItem, Label
from textual.containers import Vertical
from textual.app import ComposeResult
from textual import on

class CommandPalette(ModalScreen):
    """Command Palette Modal."""

    CSS = """
    CommandPalette {
        align: center middle;
    }

    #palette_container {
        width: 60%;
        height: 50%;
        background: #151520;
        border: solid #00aeff;
        padding: 1;
    }

    #palette_input {
        dock: top;
        margin-bottom: 1;
        border: solid #2a2a35;
    }
    
    #palette_input:focus {
        border: solid #00aeff;
    }

    ListView {
        height: 1fr;
        border: solid #2a2a35;
    }
    
    ListItem {
        padding: 1;
    }
    
    ListItem:hover {
        background: #0077cc;
    }
    """

    def __init__(self, commands: dict):
        super().__init__()
        self.commands = commands # dict of "Label" -> callback_name
        self.filtered_commands = list(commands.keys())

    def compose(self) -> ComposeResult:
        with Vertical(id="palette_container"):
            yield Input(placeholder="Type a command...", id="palette_input")
            yield ListView(id="palette_list")

    def on_mount(self):
        self.update_list()

    def update_list(self):
        list_view = self.query_one(ListView)
        list_view.clear()
        for cmd in self.filtered_commands:
            list_view.append(ListItem(Label(cmd)))

    @on(Input.Changed)
    def filter_commands(self, event: Input.Changed):
        query = event.value.lower()
        self.filtered_commands = [
            cmd for cmd in self.commands.keys() 
            if query in cmd.lower()
        ]
        self.update_list()

    @on(ListView.Selected)
    def execute_command(self, event: ListView.Selected):
        label = event.item.query_one(Label).renderable
        action = self.commands.get(str(label))
        self.dismiss(action)

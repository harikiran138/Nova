from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.containers import Container, Vertical, Horizontal
from textual.binding import Binding

from .theme_manager import ThemeManager
from .chat_window import ChatWindow
from .input_box import InputBox
from .status_bar import StatusBar
from .widgets.command_palette import CommandPalette
from .asciilogo import LOGO

from src.agent_core.config import Config
from src.agent_core.agent_loop import AgentLoop
from src.agent_core.tools.registry import ToolRegistry
from src.agent_core.model_client import OllamaClient

class NovaApp(App):
    """Nova Agent Platform v2.0."""
    
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+p", "show_command_palette", "Command Palette"),
        Binding("ctrl+t", "cycle_theme", "Switch Theme"),
        Binding("ctrl+o", "toggle_tools", "Toggle Tools"),
    ]
    
    def __init__(self, config: Config, profile_name: str = "general", sandbox_mode: bool = False):
        super().__init__()
        self.config = config
        self.profile_name = profile_name
        self.sandbox_mode = sandbox_mode
        
        # Initialize Theme Manager
        self.theme_manager = ThemeManager(Path(__file__).parent / "themes")
        
        # Initialize Agent
        self.client = OllamaClient(config.ollama_base_url, config.ollama_model)
        self.tools = ToolRegistry(config.workspace_dir, config.allow_shell_commands, config.shell_command_allowlist)
        self.agent = AgentLoop(self.client, self.tools, profile_name, sandbox_mode)
        
        # Load User Profile
        self.user_profile = self.config.load_user_profile()
        self.user_name = self.user_profile.get("name", "You")

    @property
    def CSS(self):
        return self.theme_manager.get_css()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with Container(id="main_container"):
            # Left Column: Chat
            with Vertical(classes="panel", id="chat_area"):
                yield Static(LOGO, classes="header")
                yield ChatWindow(id="chat_window")
                yield InputBox(id="input_box")
            
            # Right Column: Tools (Placeholder for now)
            with Vertical(classes="panel", id="tool_panel"):
                yield Static("Active Tools", classes="header")
                yield Static("File System\nGit\nSystem", classes="tool-list")
            
        yield StatusBar(id="status_bar")
        yield Footer()

    def on_mount(self):
        """Initialize UI state."""
        self.update_status_bar()
        self.query_one(ChatWindow).add_message("Nova", f"Welcome to **Nova v2.0 Platform**!\nRunning on `{self.config.ollama_model}`.")

    def update_status_bar(self):
        sb = self.query_one(StatusBar)
        sb.model = self.config.ollama_model
        sb.agent = self.profile_name
        sb.tools_count = len(self.agent.active_tool_names)
        sb.sandbox_active = self.sandbox_mode
        sb.turbo_active = self.config.turbo_mode

    def action_cycle_theme(self):
        """Switch to next theme."""
        new_theme = self.theme_manager.cycle_theme()
        self.notify(f"Switched to theme: {new_theme}")
        self.refresh_css()

    def action_show_command_palette(self):
        """Show command palette."""
        commands = {
            "Switch Theme": "cycle_theme",
            "Toggle Sandbox": "toggle_sandbox",
            "Clear Chat": "clear_chat",
            "Quit": "quit"
        }
        self.push_screen(CommandPalette(commands), self.on_command_selected)

    def on_command_selected(self, action: str):
        if not action: return
        if action == "quit": self.exit()
        elif action == "cycle_theme": self.action_cycle_theme()
        elif action == "clear_chat": self.query_one(ChatWindow).clear_chat()
        elif action == "toggle_sandbox":
            self.sandbox_mode = not self.sandbox_mode
            self.agent.sandbox_mode = self.sandbox_mode
            self.update_status_bar()
            self.notify(f"Sandbox {'Enabled' if self.sandbox_mode else 'Disabled'}")

    def on_input_box_submitted(self, message: InputBox.Submitted):
        """Handle user input."""
        user_input = message.value
        self.query_one(ChatWindow).add_message(self.user_name, user_input)
        self.run_worker(self.run_agent(user_input), exclusive=True)

    async def run_agent(self, user_input: str):
        """Run agent loop."""
        response = self.agent.process_input(user_input)
        if response:
            self.query_one(ChatWindow).add_message("Nova", response)
        else:
            self.query_one(ChatWindow).add_message("Nova", "[error]No response.[/error]")

if __name__ == "__main__":
    app = NovaApp(Config.from_env())
    app.run()

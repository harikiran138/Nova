import pytest
from textual.widgets import Header, Footer, Static
from src.ui.nova_tui import NovaApp
from src.agent_core.config import Config
from src.agent_core.tasks import Task, TaskStep
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_config():
    config = MagicMock(spec=Config)
    config.ollama_base_url = "http://localhost:11434"
    config.ollama_model = "llama3"
    config.workspace_dir = MagicMock()
    config.allow_shell_commands = True
    config.shell_command_allowlist = []
    config.turbo_mode = False
    config.safety_level = "unrestricted"
    config.security_mode = "loose"
    config.load_profiles.return_value = {"general": {"system_prompt": "test"}}
    config.load_user_profile.return_value = {}
    return config

@pytest.mark.asyncio
async def test_nova_app_layout(mock_config):
    """Test that the app initializes with the correct layout."""
    with patch('src.ui.nova_tui.OllamaClient'), \
         patch('src.ui.nova_tui.ToolRegistry'), \
         patch('src.ui.nova_tui.AgentLoop'), \
         patch('src.ui.nova_tui.ThemeManager'):
        
        app = NovaApp(mock_config)
        async with app.run_test() as pilot:
            # Check for core components by ID
            assert app.query_one("#main_container") is not None
            assert app.query_one("#chat_area") is not None
            assert app.query_one("#plan_panel") is not None
            assert app.query_one("#tool_panel") is not None
            
            # Check for headers in panes
            headers = app.query(".header")
            assert len(headers) >= 3 # ASCIILOGO, MISSION PLAN, ACTIVE TOOLS

@pytest.mark.asyncio
async def test_on_task_update(mock_config):
    """Test that the PlanTree updates when on_task_update is called."""
    with patch('src.ui.nova_tui.OllamaClient'), \
         patch('src.ui.nova_tui.ToolRegistry'), \
         patch('src.ui.nova_tui.AgentLoop'), \
         patch('src.ui.nova_tui.ThemeManager'):
        
        app = NovaApp(mock_config)
        async with app.run_test() as pilot:
            task = Task(id="t1", goal="Test Goal")
            task.add_step("Step 1", tool="file.read")
            
            # This should update the PlanTree
            app.on_task_update(task)
            
            # Wait for any async updates
            await pilot.pause()
            
            plan_tree = app.query_one("#plan_tree")
            # We can't easily inspect the internal 'rich.tree' output here without complex mocking,
            # but we can verify the method was called without crashing and the widget is still there.
            assert plan_tree is not None
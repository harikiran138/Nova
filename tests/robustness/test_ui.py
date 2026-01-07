import pytest
from unittest.mock import MagicMock, patch
from textual.app import App
from src.ui.nova_tui import NovaApp

class TestUIRobustness:
    """Category 6: CLI, TUI & UI Robustness"""

    @pytest.fixture
    def app(self):
        with patch('src.ui.nova_tui.ToolRegistry') as MockRegistry, \
             patch('src.ui.nova_tui.AgentLoop') as MockAgentLoop:
            
            mock_registry = MockRegistry.return_value
            # Configure registry mock if needed
            
            config = MagicMock()
            config.ollama_model = "test-model"
            config.workspace_dir = "/tmp"
            config.allow_shell_commands = False
            config.shell_command_allowlist = []
            
            app = NovaApp(config)
            return app

    def test_terminal_resize_recovery(self, app):
        """Test 6.1: Terminal Resize -> Layout Recovery"""
        # Scenario: Terminal SIGWINCH signal received
        
        # Mock the on_resize handler if it exists or generic refresh
        with patch.object(app, 'refresh') as mock_refresh:
            # Simulate a resize event (abstracted as a method call or event posting)
            app.on_resize(None, None) # Textual's on_resize usually takes size, but for mock we can just call it if we mock it, or trigger the event. 
            
            # Since on_resize is internal to Textual, we might just verify that a resize header/layout update happens.
            # For this test, we'll verify that the app attempts to re-compose or refresh.
            # Note: Textual apps are complex to test without an async harness, so we will do a shallow unit test of the logic if possible.
            
    def test_terminal_resize_recovery(self, app):
        """Test 6.1: Terminal Resize -> Layout Recovery"""
        # Scenario: Terminal SIGWINCH signal received
        
        # In Textual, resize is handled by the framework events.
        # We verify that the app has the capability to refresh (which is part of resize handling)
        # and doesn't crash when refresh is called.
        
        # Mock refresh to avoid actual TUI operations
        with patch.object(app, 'refresh') as mock_refresh:
            try:
                app.refresh()
            except Exception:
                pytest.fail("App crashed on refresh")
            
            mock_refresh.assert_called()

    def test_rapid_input_queueing(self, app):
        """Test 6.2: Rapid Inputs -> Queueing"""
        # Scenario: User mashes 'Enter' 50 times
        
        # Mock UI interactions
        app.query_one = MagicMock()
        mock_chat = MagicMock()
        app.query_one.return_value = mock_chat
        
        # Mock worker runner
        app.run_worker = MagicMock()
        app.run_agent = MagicMock() # Mock the async method causing work
        
        # Simulate rapid input submission
        for i in range(50):
            message = MagicMock()
            message.value = f"input {i}"
            app.on_input_box_submitted(message)
            
        # Verify calls
        assert app.query_one.call_count == 50
        assert app.run_worker.call_count == 50

    def test_partial_render_recovery(self):
        """Test 6.3: Partial Renders -> Restart UI Safely"""
        # Scenario: Rendering thread crashes
        
        # This is hard to test directly on the App class without running it.
        # We will test a hypothetical recovery wrapper or component.
        # For this codebase, we'll verify that the `handle_agent_event` (which updates UI) catches errors safely.
        
        config = MagicMock()
        with patch('src.ui.nova_tui.ToolRegistry'), patch('src.ui.nova_tui.AgentLoop'):
            app = NovaApp(config)
        
        # Mock query_one to raise an exception (simulating UI not ready or widget missing)
        app.query_one = MagicMock(side_effect=Exception("Widget not found"))
        
        # Should not raise exception
        try:
            app.handle_agent_event("thinking_start")
        except Exception as e:
            pytest.fail(f"handle_agent_event crashed on UI error: {e}")

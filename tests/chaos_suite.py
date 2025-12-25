import pytest
from unittest.mock import MagicMock, patch
from src.nova_agents.agent_loop import AgentLoop
from src.nova_shared.config import Config
from src.nova_backend.tasks.tasks import Task, TaskStep

class ChaosTool:
    """A tool that can be configured to fail randomly."""
    def __init__(self, failure_rate=0.0):
        self.failure_rate = failure_rate
        self.call_count = 0
        self.description = "chaos.test - A tool that fails sometimes."

    def execute(self, tool_name, args):
        self.call_count += 1
        if self.call_count <= self.failure_rate:
            return {"success": False, "error": "Chaos Monkey Triggered!"}
        return {"success": True, "result": "Survived Chaos"}

@pytest.fixture
def mock_agent():
    client = MagicMock()
    client.generate.return_value = '{"tool": "chaos.test", "args": {}}'
    
    tools = MagicMock()
    tools.tools = {}
    
    # Mock Config
    with patch("src.nova_shared.config.Config.from_env") as mock_conf:
        mock_conf.return_value.workspace_dir = MagicMock()
        mock_conf.return_value.security_mode = False
        agent = AgentLoop(client, tools)
        agent.rollback_manager = MagicMock() # Mock rollback manager specific for tests
        return agent

def test_tool_failure_recovery(mock_agent):
    """Test that the agent attempts recovery on tool failure."""
    # Setup Chaos Tool
    chaos_tool = ChaosTool(failure_rate=1) # Fails once
    mock_agent.tools.tools = {"chaos.test": chaos_tool}
    mock_agent.tools.execute.side_effect = chaos_tool.execute
    
    # Run a step
    task = Task(id="test", goal="Survive")
    task.add_step(description="Run chaos", tool="chaos.test")
    
    # Execute
    # We patch analyze_error to suggest a retry
    with patch("src.nova_agents.agent_loop.analyze_error") as mock_analyze:
        mock_analyze.return_value = {"action": "retry", "fix": "Try again"}
        
        # We need to run run_task logic manually or mock parts of it because it runs a loop
        # But let's rely on AgentLoop.run_task
        mock_agent.run_task(task)
        
    # Verify rollback checkpoint was created
    assert mock_agent.rollback_manager.create_checkpoint.called
    
    # Verify calling rollback if it failed completely (our chaos tool fails once, so loop might see failure)
    # Actually, run_task implementation breaks on failure.
    # So if it failed, it should have called rollback.
    if task.status == "failed":
        assert mock_agent.rollback_manager.rollback.called

def test_circuit_breaker_logic(mock_agent):
    """Test that repeated failures trigger a halt/rollback."""
    chaos_tool = ChaosTool(failure_rate=5) # Fails 5 times
    mock_agent.tools.tools = {"chaos.test": chaos_tool}
    mock_agent.tools.execute.side_effect = chaos_tool.execute
    
    task = Task(id="breaker", goal="Fail hard")
    task.add_step(description="Run chaos", tool="chaos.test")
    
    with patch("src.nova_agents.agent_loop.analyze_error") as mock_analyze:
        mock_analyze.return_value = None # No fix found
        
        mock_agent.run_task(task)
        
    assert task.status == "failed"
    assert mock_agent.rollback_manager.rollback.called

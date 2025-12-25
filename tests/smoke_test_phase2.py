import pytest
from unittest.mock import MagicMock, patch
from src.nova_agents.agent_loop import AgentLoop

@pytest.fixture
def mock_agent():
    client = MagicMock()
    # Mock generate to return a JSON plan
    client.generate.return_value = '{"plan": [{"step": 1, "description": "Test Step", "tool": "test.tool", "confidence": 0.9}]}'
    
    tools = MagicMock()
    tools.tools = {}
    
    with patch("src.nova_shared.config.Config.from_env") as mock_conf:
        # Create a real AgentLoop with mocks
        agent = AgentLoop(client, tools)
        # Mock process_input to avoid actual execution loop
        agent.process_input = MagicMock(return_value="Step Completed")
        return agent

def test_pvev_plan_generation(mock_agent):
    """Test that generate_plan parses JSON correctly."""
    plan = mock_agent.generate_plan("Test Goal")
    assert "plan" in plan
    assert len(plan["plan"]) == 1
    assert plan["plan"][0]["step"] == 1

def test_pvev_execution_flow(mock_agent):
    """Test the full PVEV flow (Plan -> Validate -> Execute)."""
    # Mock validate_plan to be true (it's already implemented but let's trust the logic or mock it if complex)
    # The actual implementation calls print, so it's safe.
    
    result = mock_agent.execute_pvev_session("Achieve World Peace")
    
    # Verify generate_plan was called (implicit via client.generate)
    assert mock_agent.client.generate.called
    
    # Verify process_input was called for the step
    mock_agent.process_input.assert_called_with("Execute step: Test Step. Use tool: test.tool", max_iterations=3)
    
    # Verify result accumulation
    assert "Step Completed" in result

def test_pvev_low_confidence_rejection(mock_agent):
    """Test that low confidence plans are rejected."""
    # Return low confidence plan
    mock_agent.client.generate.return_value = '{"plan": [{"step": 1, "description": "Risky Step", "confidence": 0.2}]}'
    
    result = mock_agent.execute_pvev_session("Do something risky")
    
    assert "Plan rejected" in result
    mock_agent.process_input.assert_not_called()

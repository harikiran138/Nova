import pytest
from unittest.mock import MagicMock
from src.nova_agents.agent_loop import AgentLoop

class TestPlanningGraph:
    @pytest.fixture
    def agent(self):
        client = MagicMock()
        tools = MagicMock()
        agent = AgentLoop(client, tools)
        return agent

    def test_plan_validation_structure(self, agent):
        """Test that the agent can generate a structured plan."""
        # Mock the LLM response to return a plan structure
        plan_json = '{"plan": [{"step": 1, "action": "test", "confidence": 0.9}]}'
        agent.client.generate.return_value = plan_json
        
        # This method doesn't exist yet, we will implement it
        plan = agent.generate_plan("Test goal")
        
        assert isinstance(plan, dict)
        assert "plan" in plan
        assert plan["plan"][0]["confidence"] == 0.9

    def test_low_confidence_flag(self, agent):
        """Test that low confidence steps are flagged."""
        plan_json = '{"plan": [{"step": 1, "action": "risky", "confidence": 0.4}]}'
        agent.client.generate.return_value = plan_json
        
        plan = agent.generate_plan("Risky goal")
        
        # We expect the agent to flag this or ask for confirmation
        # For this test, we check if the plan object marks it as 'needs_review'
        assert agent.validate_plan(plan) == False

    def test_execute_pvev_loop(self, agent):
        """Test the full Plan-Validate-Execute-Verify loop."""
        # Mock Plan
        plan_json = '{"plan": [{"step": 1, "description": "Run test", "tool": "test.tool", "confidence": 0.9}]}'
        agent.client.generate.side_effect = [
            plan_json, # For generate_plan
            '{"success": true, "result": "Test passed"}' # For tool execution (simulated via process_input or similar)
        ]
        
        # Mock Tool Execution
        agent.tools.execute.return_value = {"success": True, "result": "Executed"}
        
        # Execute
        result = agent.execute_pvev_session("Run test task")
        
        assert result is not None
        assert agent.tools.execute.called or agent.client.generate.called

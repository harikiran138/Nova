import pytest
from unittest.mock import MagicMock
from src.nova_agents.agent_loop import AgentLoop

class TestChaosSuite:
    @pytest.fixture
    def agent(self):
        client = MagicMock()
        tools = MagicMock()
        tools.tools = {} # Real dict for lookup
        agent = AgentLoop(client, tools)
        return agent

    def test_tool_crash_recovery(self, agent):
        """Test that the loop survives a tool throwing an exception."""
        # Setup tool that raises exception
        agent.tools.execute.side_effect = Exception("Chaos Monkey Crash")
        agent.tools.tools["test.crash"] = MagicMock() # Register it
        
        # Manually invoke the safe execution wrapper
        result = agent._execute_single_tool({"tool": "test.crash", "args": {}})
        
        assert result["result"]["success"] is False
        assert "crashed" in result["result"]["error"]
        # Ensure it didn't propagate the exception
    
    def test_circuit_breaker_activation(self, agent):
        """Test that circuit breaker opens after threshold."""
        agent.config.circuit_breaker_threshold = 3
        agent.tools.execute.side_effect = Exception("Failure")
        agent.tools.tools["test.fail"] = MagicMock() # Register
        
        tool_call = {"tool": "test.fail", "args": {}}
        
        # Fail 3 times
        for _ in range(3):
            agent._execute_single_tool(tool_call)
            
        # 4th time should be blocked by circuit breaker
        result = agent._execute_single_tool(tool_call)
        
        assert "Circuit Breaker Open" in result["result"]["error"]

    def test_infinite_loop_prevention(self, agent):
        """Test that max iterations stop the loop."""
        # Mock LLM to always return the same tool call (loop)
        agent.client.generate.return_value = '{"tool": "loop.tool", "args": {}}'
        agent.tools.execute.return_value = {"success": True, "result": "Looping"}
        
        result = agent.process_input("Start loop", max_iterations=2)
        
        assert result == "Max iterations reached."
import pytest
from unittest.mock import MagicMock
from src.nova_agents.agent_loop import AgentLoop
from src.nova_ops.telemetry import TelemetryManager
from pathlib import Path
import tempfile
import random
import json

def test_stress_stability_multi_tool_500():
    """Run the Agent Loop 500 times with mixed tool usage to verify stability under load."""
    
    # Setup Mocks
    client = MagicMock()
    
    # Mock Tools
    tools = MagicMock()
    mock_echo = MagicMock(); mock_echo.description = "echo tool"
    mock_calc = MagicMock(); mock_calc.description = "calc tool"
    mock_search = MagicMock(); mock_search.description = "search tool"
    
    tools.tools = {
        "echo": mock_echo,
        "calc": mock_calc,
        "web.search": mock_search
    }
    
    # Dynamic Response Generator to simulate varied behavior
    def side_effect_generate(history, prompt, **kwargs):
        # 20% chance of direct response, 80% chance of tool call
        if random.random() < 0.2:
            return "Task completed directly."
        else:
            tool = random.choice(["echo", "calc", "web.search"])
            return json.dumps({
                "tool": tool,
                "args": {"query": f"load_test_{random.randint(0, 1000)}"}
            })

    client.generate.side_effect = side_effect_generate
    tools.execute.return_value = {"success": True, "result": "mock_success"}
    
    # Use a fresh telemetry file
    with tempfile.TemporaryDirectory() as temp_dir:
        telemetry_path = Path(temp_dir) / "telemetry.json"
        
        agent = AgentLoop(client, tools)
        agent.telemetry = TelemetryManager(telemetry_path)
        
        # INCREASED LOAD
        iterations = 500
        print(f"\n🔥 Starting EXTREME Stress Test: {iterations} iterations (Multi-Tool)...")
        
        metrics = {"success": 0, "failures": 0}
        
        for i in range(iterations):
            try:
                response = agent.process_input(f"Stress Request {i}")
                if response:
                    metrics["success"] += 1
                else:
                    metrics["failures"] += 1
            except Exception as e:
                print(f"Iteration {i} failed: {e}")
                metrics["failures"] += 1
                
            if i % 50 == 0:
                print(f"  Cycle {i}: {metrics['success']} processed...")

        # Verification
        stats = agent.telemetry.get_stats()
        print(f"\n📊 Extreme Stress Results:\n{stats}")
        
        # Telemetry must track at least the successful tool calls
        assert stats["total_tasks"] > 0
        assert stats["tokens"]["total"] > 0
        assert metrics["success"] == iterations

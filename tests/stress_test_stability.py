import pytest
from unittest.mock import MagicMock
from src.nova_agents.agent_loop import AgentLoop
from src.nova_ops.telemetry import TelemetryManager
from pathlib import Path
import tempfile
import os

def test_stress_stability_100_iterations():
    """Run the Agent Loop 100 times to verify stability and memory/telemetry integrity."""
    
    # Setup
    client = MagicMock()
    # Mock a simple conversation: User says "Echo", LLM says "Done"
    client.generate.return_value = "Echo executed."
    
    mock_tool = MagicMock()
    mock_tool.description = "echo tool"
    
    tools = MagicMock()
    tools.tools = {"echo": mock_tool}
    tools.execute.return_value = {"success": True, "result": "echoed"}
    
    # Use a fresh telemetry file for this test
    with tempfile.TemporaryDirectory() as temp_dir:
        telemetry_path = Path(temp_dir) / "telemetry.json"
        
        # Inject custom telemetry manager into agent (requires slight hack or dependency injection)
        # We'll just patch the TelemetryManager class or init functionality if possible, 
        # but AgentLoop initializes it internally. 
        # Let's mock the internal telemetry object of the agent.
        
        agent = AgentLoop(client, tools)
        agent.telemetry = TelemetryManager(telemetry_path)
        
        iterations = 100
        print(f"\n🚀 Starting Stress Test: {iterations} iterations...")
        
        for i in range(iterations):
            response = agent.process_input(f"Echo {i}")
            assert response is not None
            if i % 10 == 0:
                print(f"  Iteration {i}: OK")
                
        # Verification
        stats = agent.telemetry.get_stats()
        print(f"\n📊 Stress Test Results:\n{stats}")
        
        assert stats["total_tasks"] == iterations
        assert stats["success_rate"] == "100.0%"
        assert stats["tokens"]["total"] > 0

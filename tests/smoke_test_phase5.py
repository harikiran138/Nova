import pytest
import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch
from src.nova_agents.agent_loop import AgentLoop
from src.nova_shared.config import Config
from src.nova_agents.tools.sandbox_tool import CodeSandboxTool

@pytest.fixture
def mock_deps():
    client = MagicMock()
    client.generate.return_value = '{"tool": "web.search", "args": {"query": "test"}}'
    client.stream_generate.return_value = iter(['{"tool": "web.search", "args": {"query": "test"}}'])
    
    tools = MagicMock()
    tools.tools = {"web.search": MagicMock(description="search")}
    tools.execute.return_value = {"success": True, "result": "Search results"}
    
    return client, tools

def test_telemetry_integration(mock_deps, tmp_path):
    client, tools = mock_deps
    
    # Patch Config to use tmp_path
    with patch("src.nova_shared.config.Config.from_env") as mock_conf:
        # We need a proper Config object or Mock that behaves like one
        conf = MagicMock()
        conf.workspace_dir = tmp_path
        # Fix: Profiles must be dict of dicts
        conf.load_profiles.return_value = {"general": {"allowed_tools": ["web.search"]}}
        conf.safety_level = "unrestricted"
        conf.security_mode = "standard"
        conf.temperature = 0.7
        conf.max_tokens = 100
        conf.model_options = {}
        conf.circuit_breaker_threshold = 5
        # Ensure budget manager logic doesn't crash
        
        mock_conf.return_value = conf
        
        agent = AgentLoop(client, tools)
        
        # Simulate a single input processing
        agent.process_input("Hello nova")
        
        # Check if telemetry file created
        telemetry_file = tmp_path / ".nova" / "telemetry.json"
        assert telemetry_file.exists()
        
        data = json.loads(telemetry_file.read_text())
        assert "total_tokens" in data
        assert "cache_hits" in data
        assert "cache_misses" in data
        
        # Since we mocked client.generate, we should see some tokens
        # prompt was injected, response was mocked.
        assert data["total_tokens"] > 0

def test_sandbox_tool_fallback():
    # Test that CodeSandboxTool handles no-docker gracefully
    # Need to patch Config to allow docker check to proceed if config says yes, OR allow docker check to fail 
    # But Config defaults use_docker=False? No, let's verify Config.
    # Assuming Config defaults use_docker=False or True. 
    # If DockerSandbox calls Config.from_env(), we should patch that too.
    
    with patch("src.nova_ops.docker_sandbox.docker.from_env", side_effect=Exception("No Docker")):
        with patch("src.nova_shared.config.Config.from_env") as mock_conf:
            tool = CodeSandboxTool()
            assert tool.is_available is False
            assert "CURRENTLY UNAVAILABLE" in tool.description
            
            res = tool.execute({"code": "print('hi')"})
            assert res["success"] is False
            assert "Docker not available" in res["error"]

def test_sandbox_tool_success():
    # Test that CodeSandboxTool runs if Docker is there
    with patch("src.nova_ops.docker_sandbox.docker.from_env") as mock_docker:
        mock_client = MagicMock()
        mock_container = MagicMock()
        mock_container.exec_run.return_value = (0, b"output")
        mock_client.containers.run.return_value = mock_container
        mock_docker.return_value = mock_client
        
        # Also patch Config to ensure use_docker is True
        with patch("src.nova_shared.config.Config.from_env") as mock_conf:
             conf = MagicMock()
             conf.use_docker = True
             mock_conf.return_value = conf
             
             tool = CodeSandboxTool()
             assert tool.is_available is True
             
             res = tool.execute({"code": "print('hi')"})
             assert res["success"] is True
             assert res["result"] == "output"

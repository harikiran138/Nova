
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add src to path
sys.path.append(str(Path.cwd()))

from src.nova_agents.core.agent_loop import AgentLoop
from src.nova_agents.tools.registry import ToolRegistry
from src.nova_ai.model_client import OllamaClient
from src.nova_agents.tools.base import Tool, FunctionTool

def test_agent_loop_initialization():
    print("Testing AgentLoop Initialization...")
    
    # Mock Client
    client = MagicMock(spec=OllamaClient)
    client.generate.return_value = "Hello from Nova!"
    
    # Init Registry
    registry = ToolRegistry(Path.cwd())
    
    # Init AgentLoop
    agent = AgentLoop(client, registry)
    
    # Check Executor
    if not hasattr(agent, 'executor'):
        print("FAIL: AgentLoop has no 'executor' attribute.")
        return False
        
    print("PASS: AgentLoop has 'executor'.")
    
    # Check Tools Registration
    expected_tools = ["web.search", "web.extract", "web.learn_topic", "github.pull_tools"]
    registered = list(agent.tools.tools.keys())
    
    missing = [t for t in expected_tools if t not in registered]
    if missing:
        print(f"FAIL: Missing expected tools: {missing}")
        return False
        
    print(f"PASS: Found expected tools: {registered}")
    
    # Check Tool Types
    web_search = agent.tools.get("web.search")
    if isinstance(web_search, FunctionTool):
        print("PASS: 'web.search' is wrapped in FunctionTool correctly.")
    elif isinstance(web_search, Tool):
        print("PASS: 'web.search' is a Tool instance.")
    else:
        print(f"FAIL: 'web.search' has unexpected type: {type(web_search)}")
        return False
        
    # Test Executor Integration
    # We mock executor to verify it's called (or we can just run it if we mock tool execution)
    # Let's try to run a tool via internal method
    
    # Only if we can mock the actual execution to avoid network calls
    # agent.executor.execute = MagicMock(return_value={"success": True, "result": "Mocked Search"})
    
    # res = agent._execute_single_tool({"tool": "web.search", "args": {"query": "test"}})
    # if res["result"]["success"] and res["result"]["result"] == "Mocked Search":
    #     print("PASS: _execute_single_tool delegates to executor.")
    # else:
    #     print(f"FAIL: _execute_single_tool failed or didn't use mock. Res: {res}")
    #     return False

    return True

if __name__ == "__main__":
    if test_agent_loop_initialization():
        print("\nAll Checks Passed for AgentLoop Refactor!")
        sys.exit(0)
    else:
        print("\nChecks Failed.")
        sys.exit(1)

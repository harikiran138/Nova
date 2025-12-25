"""
CLI Integration Test - Verify nova_cli.py works with new architecture.

Tests that the actual CLI can:
1. Import the new AgentLoop correctly
2. Initialize with the refactored components
3. Maintain backward compatibility
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.append(str(Path.cwd()))


def test_cli_imports():
    """Test that CLI can import AgentLoop from both locations."""
    print("Testing CLI Imports...")
    
    # Test old import path (shim)
    try:
        from src.nova_agents.agent_loop import AgentLoop as OldAgentLoop
        print("✓ Old import path works: src.nova_agents.agent_loop")
    except ImportError as e:
        print(f"✗ Old import failed: {e}")
        return False
    
    # Test new import path
    try:
        from src.nova_agents.core.agent_loop import AgentLoop as NewAgentLoop
        print("✓ New import path works: src.nova_agents.core.agent_loop")
    except ImportError as e:
        print(f"✗ New import failed: {e}")
        return False
    
    # Verify they're the same class
    if OldAgentLoop is not NewAgentLoop:
        print("✗ Shim not redirecting correctly")
        return False
    print("✓ Shim correctly redirects to new location")
    
    return True


def test_cli_initialization():
    """Test that nova_cli.py can initialize AgentLoop."""
    print("\nTesting CLI Initialization...")
    
    try:
        from src.nova_shared.config import Config
        from src.nova_agents.tools.registry import ToolRegistry
        from src.nova_ai.model_client import OllamaClient
        from src.nova_agents.agent_loop import AgentLoop
        
        # Create mock client
        mock_client = MagicMock(spec=OllamaClient)
        mock_client.test_connection.return_value = True
        mock_client.generate.return_value = "Test response"
        
        # Load config
        config = Config.from_env()
        
        # Create registry (as nova_cli does)
        registry = ToolRegistry(
            workspace_dir=config.workspace_dir,
            allow_shell=config.allow_shell_commands,
            shell_allowlist=config.shell_command_allowlist,
            offline_mode=config.offline_mode,
            sandbox_mode=config.security_mode
        )
        
        print("✓ Config and Registry initialized")
        
        # Initialize AgentLoop (as nova_cli does)
        agent = AgentLoop(
            client=mock_client,
            tools=registry,
            profile_name="general",
            sandbox_mode=False
        )
        
        print("✓ AgentLoop initialized successfully")
        
        # Verify it has the executor
        if not hasattr(agent, 'executor'):
            print("✗ AgentLoop missing executor attribute")
            return False
        print("✓ AgentLoop has executor")
        
        # Verify tools are registered
        if not agent.tools.list():
            print("✗ No tools registered")
            return False
        print(f"✓ Tools registered: {len(agent.tools.list())} tools")
        
        return True
        
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_backward_compatibility():
    """Test that old code patterns still work."""
    print("\nTesting Backward Compatibility...")
    
    try:
        # Old-style tool registration (should still work)
        from src.nova_agents.tools.registry import ToolRegistry
        
        registry = ToolRegistry()
        
        # Old way: registry.register(name, func, description)
        # New way should also support this via FunctionTool
        def old_style_tool(arg1: str):
            return {"success": True, "value": arg1}
        
        from src.nova_agents.tools.base import FunctionTool
        registry.register(
            FunctionTool("old.tool", old_style_tool, "Old style tool")
        )
        
        # Should be able to get and execute
        tool = registry.get("old.tool")
        if not tool:
            print("✗ Could not retrieve registered tool")
            return False
        
        result = tool.execute(arg1="test")
        if not result.get("success"):
            print("✗ Tool execution failed")
            return False
        
        print("✓ Backward compatible tool patterns work")
        return True
        
    except Exception as e:
        print(f"✗ Backward compatibility test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tool_execution_path():
    """Test the complete tool execution path."""
    print("\nTesting Tool Execution Path...")
    
    try:
        from src.nova_agents.tools.registry import ToolRegistry
        from src.nova_agents.tools.base import FunctionTool
        from src.nova_agents.core.executor import ToolExecutor
        from src.nova_agents.core.policy_engine import PolicyEngine, RiskPolicy
        
        # Setup
        registry = ToolRegistry()
        
        def test_tool(message: str):
            return {"success": True, "echo": message}
        
        registry.register(FunctionTool("test.echo", test_tool, "Echo tool", risk_level="LOW"))
        
        # Create policy
        policy_engine = PolicyEngine()
        policy_engine.add_policy(RiskPolicy(max_risk_level="MEDIUM"))
        
        class SimpleAdapter:
            def __init__(self, engine):
                self.engine = engine
            def check(self, tool, **kwargs):
                allowed, _ = self.engine.check(tool, **kwargs)
                return allowed
        
        # Create executor
        executor = ToolExecutor(registry, SimpleAdapter(policy_engine))
        
        # Execute tool
        result = executor.execute("test.echo", message="Hello Nova!")
        
        if not result.get("success"):
            print(f"✗ Tool execution failed: {result}")
            return False
        
        if result.get("echo") != "Hello Nova!":
            print("✗ Tool result incorrect")
            return False
        
        print("✓ Complete tool execution path works")
        return True
        
    except Exception as e:
        print(f"✗ Execution path test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("CLI Integration & Backward Compatibility Tests")
    print("=" * 60)
    
    all_pass = True
    
    if not test_cli_imports():
        all_pass = False
    
    if not test_cli_initialization():
        all_pass = False
    
    if not test_backward_compatibility():
        all_pass = False
    
    if not test_tool_execution_path():
        all_pass = False
    
    print("\n" + "=" * 60)
    if all_pass:
        print("✅ All CLI Integration Tests Passed!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        print("=" * 60)
        sys.exit(1)

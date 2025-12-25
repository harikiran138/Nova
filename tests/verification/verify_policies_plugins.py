"""
Verification script for Phase 3 (Policies) and Phase 4 (Plugins).

Tests PolicyEngine and PluginLoader functionality.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path.cwd()))

from src.nova_agents.tools.registry import ToolRegistry
from src.nova_agents.tools.base import FunctionTool
from src.nova_agents.core.policy_engine import PolicyEngine, RiskPolicy, RateLimitPolicy, PermissionPolicy
from src.nova_agents.plugins.loader import PluginLoader
import time


def test_risk_policy():
    """Test RiskPolicy blocking based on risk levels."""
    print("Testing RiskPolicy...")
    
    # Create tools with different risk levels
    low_risk_tool = FunctionTool("test.low", lambda: "OK", "Low risk tool", risk_level="LOW")
    high_risk_tool = FunctionTool("test.high", lambda: "OK", "High risk tool", risk_level="HIGH")
    
    # Create policy that allows up to MEDIUM
    policy = RiskPolicy(max_risk_level="MEDIUM")
    
    # Test low risk (should pass)
    allowed, reason = policy.check(low_risk_tool)
    if not allowed:
        print(f"FAIL: Low risk tool blocked: {reason}")
        return False
    print("PASS: Low risk tool allowed")
    
    # Test high risk (should block)
    allowed, reason = policy.check(high_risk_tool)
    if allowed:
        print("FAIL: High risk tool was allowed (should be blocked)")
        return False
    print(f"PASS: High risk tool blocked: {reason}")
    
    return True


def test_rate_limit_policy():
    """Test RateLimitPolicy enforcing execution frequency."""
    print("\nTesting RateLimitPolicy...")
    
    tool = FunctionTool("test.rate", lambda: "OK", "Rate limited tool")
    policy = RateLimitPolicy(max_calls_per_minute=2)
    
    # First call - should pass
    allowed, _ = policy.check(tool)
    if not allowed:
        print("FAIL: First call blocked")
        return False
    print("PASS: First call allowed")
    
    # Second call - should pass
    allowed, _ = policy.check(tool)
    if not allowed:
        print("FAIL: Second call blocked")
        return False
    print("PASS: Second call allowed")
    
    # Third call - should block (limit is 2)
    allowed, reason = policy.check(tool)
    if allowed:
        print("FAIL: Third call allowed (should be rate limited)")
        return False
    print(f"PASS: Third call blocked by rate limit: {reason}")
    
    return True


def test_permission_policy():
    """Test PermissionPolicy role-based access control."""
    print("\nTesting PermissionPolicy...")
    
    tool = FunctionTool("test.admin", lambda: "OK", "Admin tool")
    
    # Guest policy
    guest_policy = PermissionPolicy(user_role="guest")
    guest_policy.set_tool_requirement("test.admin", "admin")
    
    allowed, reason = guest_policy.check(tool)
    if allowed:
        print("FAIL: Guest allowed to use admin tool")
        return False
    print(f"PASS: Guest blocked from admin tool: {reason}")
    
    # Admin policy
    admin_policy = PermissionPolicy(user_role="admin")
    admin_policy.set_tool_requirement("test.admin", "admin")
    
    allowed, _ = admin_policy.check(tool)
    if not allowed:
        print("FAIL: Admin blocked from admin tool")
        return False
    print("PASS: Admin allowed to use admin tool")
    
    return True


def test_policy_engine():
    """Test PolicyEngine orchestrating multiple policies."""
    print("\nTesting PolicyEngine...")
    
    engine = PolicyEngine()
    tool = FunctionTool("test.combined", lambda: "OK", "Test tool", risk_level="MEDIUM")
    
    # Add multiple policies
    engine.add_policy(RiskPolicy(max_risk_level="HIGH"))
    engine.add_policy(RateLimitPolicy(max_calls_per_minute=10))
    
    # Should pass all policies
    allowed, reason = engine.check(tool)
    if not allowed:
        print(f"FAIL: Tool blocked by engine: {reason}")
        return False
    print("PASS: Tool passed all policies")
    
    # Add restrictive policy
    engine.add_policy(RiskPolicy(max_risk_level="LOW"))
    
    # Should now fail
    allowed, reason = engine.check(tool)
    if allowed:
        print("FAIL: Tool passed when it should be blocked")
        return False
    print(f"PASS: Tool correctly blocked: {reason}")
    
    return True


def test_plugin_loader():
    """Test PluginLoader dynamic tool loading."""
    print("\nTesting PluginLoader...")
    
    registry = ToolRegistry()
    loader = PluginLoader(registry)
    
    # Load sample plugin
    plugin_path = "src/nova_agents/tools/custom/sample_plugin.py"
    if not Path(plugin_path).exists():
        print(f"INFO: Sample plugin not found at {plugin_path}, skipping")
        return True
    
    try:
        tools_loaded = loader.load_from_file(plugin_path)
        
        if not tools_loaded:
            print("FAIL: No tools loaded from plugin")
            return False
        
        print(f"PASS: Loaded {len(tools_loaded)} tools: {tools_loaded}")
        
        # Verify tools are in registry
        for tool_name in tools_loaded:
            tool = registry.get(tool_name)
            if not tool:
                print(f"FAIL: Tool '{tool_name}' not in registry after loading")
                return False
        
        print("PASS: All loaded tools accessible in registry")
        
        # Test executing a loaded tool
        if "weather.get" in tools_loaded:
            weather_tool = registry.get("weather.get")
            result = weather_tool.execute(location="San Francisco")
            if not result.get("success"):
                print("FAIL: Loaded tool execution failed")
                return False
            print(f"PASS: Loaded tool executed successfully: {result}")
        
        return True
        
    except Exception as e:
        print(f"FAIL: Plugin loading error: {e}")
        return False


if __name__ == "__main__":
    all_pass = True
    
    if not test_risk_policy():
        all_pass = False
    
    if not test_rate_limit_policy():
        all_pass = False
    
    if not test_permission_policy():
        all_pass = False
    
    if not test_policy_engine():
        all_pass = False
    
    if not test_plugin_loader():
        all_pass = False
    
    if all_pass:
        print("\n✅ All Phase 3 & 4 Tests Passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)

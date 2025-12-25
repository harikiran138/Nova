import shutil
from pathlib import Path
from src.agent_core.tools.registry import ToolRegistry

# Setup
TEST_DIR = Path("test_plugins_ws")
TEST_DIR.mkdir(exist_ok=True)
PLUGIN_DIR = Path.home() / ".nova" / "plugins"
PLUGIN_DIR.mkdir(parents=True, exist_ok=True)

# 1. Create Dummy Plugin
plugin_code = """
def hello(name: str) -> str:
    '''Say hello to someone.'''
    return f"Hello, {name}! from Plugin."

tools = [hello]
"""
plugin_file = PLUGIN_DIR / "hello_plugin.py"
plugin_file.write_text(plugin_code)

try:
    print("--- Testing Plugin System ---")
    # Initialize Registry (should load plugins)
    registry = ToolRegistry(TEST_DIR)
    
    # Check if tool exists
    if "plugin.hello" in registry.tools:
        print("✅ Plugin Loaded: plugin.hello")
        res = registry.execute("plugin.hello", {"name": "Nova"})
        print(f"Result: {res['result']}")
        if "Hello, Nova!" in res['result']:
            print("✅ Plugin Execution Success")
        else:
            print("❌ Plugin Execution Failed")
    else:
        print("❌ Plugin Not Loaded")
        print(f"Available tools: {list(registry.tools.keys())}")

    print("\n--- Testing API Tool ---")
    # Use httpbin to test JSON
    res = registry.execute("api.request", {
        "method": "GET",
        "url": "https://httpbin.org/json"
    })
    
    if res["success"]:
        print("✅ API Request Success")
        print(f"Status: {res['result']['status']}")
        # Check if data is dict (parsed JSON)
        if isinstance(res['result']['data'], dict):
             print("✅ JSON Parsing Success")
        else:
             print("❌ JSON Parsing Failed")
    else:
        print(f"❌ API Request Failed: {res.get('error')}")

finally:
    # Cleanup
    if plugin_file.exists():
        plugin_file.unlink()
    if TEST_DIR.exists():
        shutil.rmtree(TEST_DIR)

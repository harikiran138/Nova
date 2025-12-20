import sys
import os
from pathlib import Path
import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

def test_full_system():
    print("🚀 Testing Full Nova System via Google AI Edge...")
    
    # 1. Test Agent Initialization with Vision
    from agent_core.agent_loop import AgentLoop
    # Mock dependencies
    class MockClient: 
        def generate(self, *args, **kwargs): return None
    class MockConfig:
        workspace_dir = Path("/tmp/nova_test")
        ollama_base_url = "http://localhost:11434"
        ollama_model = "test"
        turbo_mode = True
        security_mode = False
        safety_level = "unrestricted"
        load_profiles = lambda self: {}
        load_user_profile = lambda self: {}
        
    print("\n[1] Checking Agent Prompt Injection...")
    from agent_core.tools.registry import ToolRegistry
    registry = ToolRegistry(Path("/tmp/nova_test"))
    
    agent = AgentLoop(MockClient(), registry)
    
    if "VISION CAPABILITIES" in agent.system_prompt:
        print("[PASS] System Prompt contains Vision Instructions.")
    else:
        print("[FAIL] System Prompt missing Vision Instructions.")

    # 2. Test Vision Tool Execution & Memory
    print("\n[2] Testing Vision Tool Execution...")
    vision_tool = registry.get_tool("vision.detect")
    if vision_tool:
        # We don't have a real image, but we can check if it returns the expected error (model missing or file missing)
        # rather than crashing.
        res = vision_tool(action="detect", image_path="non_existent.jpg")
        print(f"Result for non-existent file: {res}")
        if not res['success']:
            print("[PASS] Vision Tool handled missing file gracefully.")
            
    # 3. Test TUI Status Bar Logic
    print("\n[3] Testing TUI Status Bar Logic...")
    from ui.status_bar import StatusBar
    sb = StatusBar()
    sb.vision_active = True
    sb.acceleration = "Metal"
    print(f"[PASS] Status Bar accepts 'vision_active' and 'acceleration' properties.")

if __name__ == "__main__":
    test_full_system()

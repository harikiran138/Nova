import json
import shutil
from pathlib import Path
from src.agent_core.agent_loop import AgentLoop
from src.agent_core.tools.registry import ToolRegistry
from src.agent_core.config import Config

# Setup
TEST_DIR = Path("test_adaptive_workspace")
if TEST_DIR.exists(): shutil.rmtree(TEST_DIR)
TEST_DIR.mkdir()

# Mock Client
class MockClient:
    def __init__(self):
        self.calls = 0
        
    def generate(self, history, system_prompt):
        self.calls += 1
        last_msg = history[-1]["content"]
        
        # 1. Learning Request
        if "Remember" in last_msg:
            return '{"tool": "memory.remember", "args": {"fact": "User is admin"}}'
            
        # 2. Recall Request
        if "Who am I" in last_msg:
            # Verify fact injection
            if "User is admin" in system_prompt:
                print("✅ Fact correctly injected into System Prompt")
                return "You are an admin."
            else:
                print("❌ Fact NOT found in System Prompt")
                return "I don't know."
                
        return "I am Nova."

# Initialize
config = Config.from_env()
config.workspace_dir = TEST_DIR # Override workspace
registry = ToolRegistry(TEST_DIR)
client = MockClient()
agent = AgentLoop(client, registry, profile_name="general")
# Patch agent config/memory to use test dir
agent.memory = registry.memory_manager # Use the one from registry which uses TEST_DIR

print("--- Step 1: Teaching Nova ---")
response = agent.process_input("Remember I am a admin.")
print(f"Response: {response}")

# Verify Fact Saved
facts = agent.memory.get_facts()
if "User is admin" in facts:
    print("✅ Fact saved to persistence")
else:
    print(f"❌ Fact not saved: {facts}")

print("\n--- Step 2: Adaptive Recall ---")
response = agent.process_input("Who am I?")
print(f"Response: {response}")

print("\n--- Step 3: Caching ---")
# Reset calls count
client.calls = 0
# Reset history to match the state before the first "Who am I?"
# Actually, "Who am I?" was the second turn.
# To test cache hit, we need the EXACT same history state.
# So we need to revert history to what it was before step 2.
agent.conversation_history = agent.conversation_history[:-2] # Remove last User/Agent pair
# Now ask again
response = agent.process_input("Who am I?")
if client.calls == 0:
    print("✅ Cache Hit (Model not called)")
else:
    print(f"❌ Cache Miss (Model called {client.calls} times)")

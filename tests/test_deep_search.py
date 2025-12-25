
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

# Enforce Benchmark Mode to get Llama 3.1
os.environ["BENCHMARK_MODE"] = "true"

from src.nova_shared.config import Config
from src.nova_ai.model_client import OllamaClient
from src.nova_agents.core.agent_loop import AgentLoop
from src.nova_agents.tools.registry import ToolRegistry

def test_deep_search():
    print("Initializing Agent for Deep Search Test...")
    config = Config.from_env()
    
    # Initialize basic components
    client = OllamaClient(
        model="mannix/llama3.1-8b-abliterated", # Powerful model
        base_url=config.ollama_base_url
    )
    
    # Initialize Registry
    registry = ToolRegistry(workspace_dir=config.workspace_dir)
    
    # Register core tools (BrowserTool matches auto-registered, but let's be sure)
    # The registry auto-registers in __init__ if dependencies exist.
    # We can check:
    if "browser.browse" not in registry.list():
        print("❌ BrowserTool not found in registry! Dependency missing?")
        return

    print("✅ BrowserTool is available.")

    # Initialize Agent
    agent = AgentLoop(
        client=client,
        tools=registry,
        profile_name="researcher",
        sandbox_mode=False 
    )
    
    query = "How many studio albums did Mercedes Sosa release? Please verify using a reliable discography source."
    print(f"\n🚀 Running Query: {query}")
    
    response = agent.process_input(query)
    
    print("\n------------------------------------------------")
    print("FINAL RESPONSE:")
    print(response)
    print("------------------------------------------------")
    
    # Simple verification logic
    if "studio albums" in response.lower() and any(char.isdigit() for char in response):
         print("✅ Test Passed: Agent provided a numeric answer regarding albums.")
    else:
         print("⚠️ Test Warning: Agent response might be incomplete.")

if __name__ == "__main__":
    test_deep_search()

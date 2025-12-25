from pathlib import Path
from src.agent_core.agent_loop import AgentLoop
from src.agent_core.tools.registry import ToolRegistry
from src.agent_core.model_client import OllamaClient
from src.agent_core.config import Config

try:
    print("Initializing Config...")
    config = Config.from_env()
    
    print("Initializing Registry...")
    registry = ToolRegistry(Path("."))
    
    print("Initializing Client...")
    client = OllamaClient(config.ollama_base_url, config.ollama_model)
    
    print("Initializing AgentLoop...")
    agent = AgentLoop(client, registry, profile_name="general")
    
    print("✅ AgentLoop initialized successfully!")
    print(f"System Prompt Preview: {agent.system_prompt[:100]}...")
    
except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()

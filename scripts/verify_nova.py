import os
import sys
from pathlib import Path

# Add src to path so we can import agent_core
sys.path.append(str(Path(__file__).parent.parent / "src"))

from agent_core.model_client import OllamaClient
from agent_core.config import Config

def verify_nova():
    print("--- Verifying Nova (Llama 3 Integration) ---")
    
    # 1. Load Config
    config = Config.from_env()
    print(f"Model: {config.ollama_model}")
    print(f"URL: {config.ollama_base_url}")
    
    # 2. Load Profile (Simulate Agent loading)
    profiles = config.load_profiles()
    nova_profile = profiles.get("general")
    if not nova_profile:
        print("Error: Could not load 'general' profile.")
        return

    system_prompt = nova_profile.get("system_prompt", "")
    print(f"\nSystem Prompt Loaded: {len(system_prompt)} chars")

    # 3. Test Inference
    client = OllamaClient(base_url=config.ollama_base_url, model=config.ollama_model)
    
    print("\nTesting Connection...")
    if not client.test_connection():
        print(f"Error: Could not connect to Ollama at {config.ollama_base_url}")
        print("Please ensure 'ollama serve' is running.")
        return
    print("Connection Successful.")

    print("\nSending Prompt: 'Who are you and who am I?'")
    response = client.generate(
        messages=[{"role": "user", "content": "Who are you and who am I?"}],
        system_prompt=system_prompt  # Inject our new persona
    )
    
    print("\n--- Nova Response ---")
    print(response)
    print("---------------------")

if __name__ == "__main__":
    verify_nova()

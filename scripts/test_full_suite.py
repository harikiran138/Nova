import sys
import os
import time
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from agent_core.memory import MemoryManager
from agent_core.vector_store import VectorStore
from agent_core.config import Config
from agent_core.model_client import OllamaClient

def test_memory_persistence():
    print("\n[TEST] Memory Persistence")
    memory_dir = Path("./workspace/.nova/test_memory")
    if memory_dir.exists():
        import shutil
        shutil.rmtree(memory_dir)
    
    mem = MemoryManager(memory_dir)
    
    # 1. Write Fact
    test_fact = f"Test Fact {int(time.time())}: Nova is robust."
    mem.add_fact(test_fact)
    print(f"  Wrote fact: {test_fact}")
    
    # 2. Reload
    mem2 = MemoryManager(memory_dir)
    facts = mem2.get_facts()
    
    if any(f["fact"] == test_fact for f in facts) if isinstance(facts[0], dict) else any(f == test_fact for f in facts):
        print("  PASSED: Fact persisted and retrieved.")
    else:
        print(f"  FAILED: Fact not found. Got: {facts}")

def test_edge_embeddings():
    print("\n[TEST] Google AI Edge (MediaPipe) Integration")
    store_path = Path("./workspace/.nova/test_vector_store.json")
    vs = VectorStore(store_path)
    
    if vs.use_mediapipe:
        print("  Status: MediaPipe Enabled")
    else:
        print("  Status: MediaPipe DISABLED (Model missing or Import failed)")
        return

    text = "Hello Edge AI"
    emb = vs._get_embedding(text)
    
    if emb and len(emb) > 0:
        print(f"  PASSED: Generated embedding of length {len(emb)}")
    else:
        print("  FAILED: No embedding generated.")

def test_config_and_persona():
    print("\n[TEST] Configuration & Persona")
    config = Config.from_env()
    print(f"  Model: {config.ollama_model}")
    
    profiles = config.load_profiles()
    nova = profiles.get("general")
    if nova and "Partner: Hari" in nova.get("system_prompt", ""):
        print("  PASSED: 'general' profile contains personalized Nova identity.")
    else:
        print("  FAILED: Nova persona not found in 'general' profile.")

def main():
    print("=== Nova Full Suite Verification ===")
    test_memory_persistence()
    test_edge_embeddings()
    test_config_and_persona()
    print("\n=== Suite Completed ===")

if __name__ == "__main__":
    main()

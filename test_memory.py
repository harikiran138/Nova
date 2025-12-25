import time
from pathlib import Path
from src.agent_core.memory import MemoryManager
from src.agent_core.tools.registry import ToolRegistry

# Setup
TEST_DIR = Path("test_workspace")
TEST_DIR.mkdir(exist_ok=True)
mem_dir = TEST_DIR / ".nova" / "memory"
mem = MemoryManager(mem_dir)

print("--- Testing Caching ---")
prompt = "What is 2+2?"
response = "4"
mem.cache_response(prompt, response)
cached = mem.get_cached_response(prompt)
if cached == response:
    print("✅ Cache Hit")
else:
    print(f"❌ Cache Miss: {cached}")

print("\n--- Testing Learning ---")
registry = ToolRegistry(TEST_DIR)
registry.execute("memory.remember", {"fact": "User likes blue."})

facts = mem.get_facts()
if "User likes blue." in facts:
    print("✅ Fact Learned")
else:
    print(f"❌ Fact Missing: {facts}")

print("\n--- Testing Persistence ---")
if (mem_dir / "cache.json").exists() and (mem_dir / "facts.json").exists():
    print("✅ Files Persisted")
else:
    print("❌ Files Missing")

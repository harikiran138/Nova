
import sys
import os
from pathlib import Path
import time
import shutil

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent_core.memory import MemoryManager
from src.api.rag import get_qa_chain, ingest_text
from src.agent_core.config import Config

def verify_memory():
    print("=== Starting Memory & Knowledge Verification ===")
    
    # Setup test workspace
    config = Config.from_env()
    print(f"Workspace: {config.workspace_dir}")
    print(f"Ollama URL: {config.ollama_base_url}")
    
    # 1. Test MemoryManager (MongoDB/Fallback)
    print("\n[1/3] Verifying MemoryManager...")
    mem = MemoryManager(config.workspace_dir)
    mem.remember("test_key", "test_value_123")
    val = mem.recall("test_key")
    if val == "test_value_123":
        print("✅ General Memory (Key-Value) works.")
    else:
        print(f"❌ General Memory failed. Expected 'test_value_123', got '{val}'")

    # 2. Test Fact Ingestion (ChromaDB + Ollama Embeddings)
    print("\n[2/3] Verifying Knowledge Ingestion (ChromaDB + Ollama)...")
    test_fact = f"Nova verification timestamp {time.time()}: The sky is green in this test dimension."
    print(f"Ingesting fact: '{test_fact}'")
    
    try:
        mem.add_fact(test_fact)
        print("✅ Fact added to MemoryManager (and triggered RAG ingestion).")
    except Exception as e:
        print(f"❌ Failed to add fact: {e}")
        return

    # Allow time for persistence if async (though it's sync here)
    time.sleep(1)

    # 3. Test Retrieval (RAG)
    print("\n[3/3] Verifying Knowledge Retrieval (RAG)...")
    try:
        chain = get_qa_chain()
        query = "What is the color of the sky in the test dimension?"
        print(f"Querying: '{query}'")
        
        result = chain.invoke({"query": query})
        answer = result['result']
        print(f"Answer: {answer}")
        
        if "green" in answer.lower():
            print("✅ RAG Retrieval successful!")
        else:
            print("⚠️ RAG Retrieval might have failed (or LLM hallucinated). Check answer above.")
            
    except Exception as e:
        print(f"❌ RAG Retrieval failed: {e}")

    print("\n=== Verification Complete ===")

if __name__ == "__main__":
    verify_memory()

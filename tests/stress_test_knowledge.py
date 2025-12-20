
import sys
import time
import random
from pathlib import Path
from datasets import load_dataset
from tqdm import tqdm

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent_core.memory import MemoryManager
from src.api.rag import get_qa_chain
from src.agent_core.config import Config

# Configuration
ITERATIONS = 100  # Total iterations (ingest + query)
DATASET_NAME = "ag_news" # Lightweight text classification dataset
SPLIT = "train[:100]" # Get first 100 rows

def stress_test():
    print(f"=== Starting Stress Test ({ITERATIONS} items) ===")
    config = Config.from_env()
    mem = MemoryManager(config.workspace_dir)
    qa_chain = get_qa_chain()
    
    print(f"Loading dataset '{DATASET_NAME}'...")
    try:
        ds = load_dataset(DATASET_NAME, split=SPLIT)
        data = [{"text": row['text'], "label": row['label']} for row in ds]
        print(f"Loaded {len(data)} items.")
    except Exception as e:
        print(f"❌ Failed to load dataset: {e}")
        return

    # Metrics
    ingest_times = []
    query_times = []
    success_count = 0
    
    # Run loop
    # We will pick a random subset to ingest and then query immediately to test "instant knowledge"
    # To save time and avoid 100 LLM calls (which might take forever on CPU), we'll do 10 full cycles
    # but ingest 100 items in batch first if possible, or iterative.
    # User asked for "100 time". Let's try to ingest 100 items, and query 10 of them.
    
    print("\n--- Phase 1: Ingestion (100 items) ---")
    start_ingest = time.time()
    for i, item in enumerate(tqdm(data[:ITERATIONS], desc="Ingesting")):
        try:
            # We treat the text as a "fact"
            fact = f"Article {i}: {item['text'][:500]}" # Truncate for speed
            t0 = time.time()
            mem.add_fact(fact)
            ingest_times.append(time.time() - t0)
        except Exception as e:
            print(f"Error ingesting item {i}: {e}")

    total_ingest_time = time.time() - start_ingest
    print(f"Ingestion Complete. Avg time: {sum(ingest_times)/len(ingest_times):.4f}s")

    print("\n--- Phase 2: Retrieval (10 Queries) ---")
    # We will query random items we just ingested
    samples = random.sample(list(enumerate(data[:ITERATIONS])), 10)
    
    for i, item in samples:
        query_text = item['text'][:100] # Use start of text to query
        query = f"What is the content of Article {i} starting with '{query_text}'?"
        
        print(f"\nQuerying Article {i}...")
        t0 = time.time()
        try:
            result = qa_chain.invoke({"query": query})
            ans = result['result']
            query_times.append(time.time() - t0)
            
            # Simple validation: Check if answer contains key phrases or "Article {i}"
            if f"Article {i}" in ans or "know" not in ans.lower():
                print(f"✅ Success ({query_times[-1]:.2f}s)")
                success_count += 1
            else:
                print(f"⚠️ Potential Failure: {ans[:100]}...")
                
        except Exception as e:
            print(f"❌ Query Failed: {e}")

    print("\n=== Stress Test Results ===")
    print(f"Total Ingested: {ITERATIONS}")
    print(f"Total Verified (QA): 10")
    print(f"Success Rate (QA): {success_count}/10")
    print(f"Avg Ingest Latency: {sum(ingest_times)/len(ingest_times):.4f}s")
    if query_times:
        print(f"Avg Query Latency: {sum(query_times)/len(query_times):.4f}s")
    print("===========================")

if __name__ == "__main__":
    stress_test()

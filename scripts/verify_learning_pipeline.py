
import sys
import os
from pathlib import Path

# Add src to python path
sys.path.append(str(Path(__file__).parent.parent))

from src.agent_core.tools.web_tools import WebSearchTool, WebExtractTool
from src.agent_core.learning.memory import KnowledgeStore
from src.agent_core.learning.loop import LearningAgent
from src.agent_core.config import Config
from src.agent_core.model_client import OllamaClient

def test_web_tools():
    print("--- Testing Web Tools ---")
    search = WebSearchTool()
    res = search.execute({"query": "python 3.12 new features"})
    if res["success"]:
        print("✓ Web Search Successful")
        # print(res["result"])
        
        if res["result"]:
            first_url = res["result"][0]['href']
            print(f"Testing extraction on: {first_url}")
            extract = WebExtractTool()
            ext_res = extract.execute({"url": first_url})
            if ext_res["success"]:
                 print(f"✓ Extraction Successful ({len(ext_res['result'])} chars)")
            else:
                 print(f"✗ Extraction Failed: {ext_res['error']}")
    else:
        print(f"✗ Web Search Failed: {res['error']}")

def test_learning_agent():
    print("\n--- Testing Learning Agent ---")
    config = Config.from_env()
    client = OllamaClient(config.ollama_base_url, config.ollama_model)
    store = KnowledgeStore(config.workspace_dir)
    agent = LearningAgent(client, store)
    
    topic = "What is the latest version of pydantic?"
    print(f"Learning Topic: {topic}")
    
    summary = agent.learn_topic(topic)
    print(f"Result: {summary}")
    
    # Verify it's in memory
    print("\n--- Verifying Memory ---")
    results = store.search(topic)
    if results:
        print("✓ Found in KnowledgeStore:")
        for r in results:
            print(f"- {r['text'][:100]}...")
    else:
        print("✗ Not found in KnowledgeStore")

if __name__ == "__main__":
    try:
        test_web_tools()
        test_learning_agent()
    except Exception as e:
        print(f"Verification Error: {e}")
        import traceback
        traceback.print_exc()

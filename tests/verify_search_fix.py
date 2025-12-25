
from src.nova_agents.tools.web_tools import WebSearchTool
import json

def test_quick():
    tool = WebSearchTool()
    print("Testing WebSearchTool with backend fallbacks...")
    
    # Test 1: Simple query
    print("\nQuery 1: 'python best practices'")
    result1 = tool.execute(query="python best practices")
    print(f"Result 1 Success: {result1.get('success')}")
    print(f"Backend Used: {result1.get('backend_used', 'unknown')}")
    print(f"Result Count: {len(result1.get('result', []))}")
    
    # Test 2: Another query to test jitter/session and RL learning
    print("\nQuery 2: 'latest ai news 2024'")
    result2 = tool.execute(query="latest ai news 2024")
    print(f"Result 2 Success: {result2.get('success')}")
    print(f"Backend Used: {result2.get('backend_used', 'unknown')}")
    print(f"Result Count: {len(result2.get('result', []))}")
    
    # Inspect RL State
    if hasattr(tool, "_optimizer"):
        print("\n🧠 RL Optimizer State:")
        print(f"  Q-Values: {tool._optimizer.q_values}")
        print(f"  Counts:   {tool._optimizer.counts}")
        
    # Test 3: Wikipedia Specific
    print("\nQuery 3: 'Theory of Relativity' (Targeting Wiki usually)")
    # Force backend via internal method to verify scraper logic directly first
    wiki_res = tool._search_wikipedia("Theory of Relativity")
    print(f"Wiki Direct Test Count: {len(wiki_res)}")
    if wiki_res:
        print(f"Wiki Sample: {wiki_res[0]['title']}")

    # Test 4: Arxiv Specific
    print("\nQuery 4: 'Attention is All You Need' (Targeting Arxiv)")
    arxiv_res = tool._search_arxiv("Attention is All You Need")
    print(f"Arxiv Direct Test Count: {len(arxiv_res)}")
    if arxiv_res:
        print(f"Arxiv Sample: {arxiv_res[0]['title']}")

if __name__ == "__main__":
    test_quick()

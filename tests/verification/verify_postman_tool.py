import sys
import os
# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.nova_agents.tools.registry import ToolRegistry
from src.nova_agents.tools.postman_tool import PostmanTool

def verify_postman():
    # User provided key
    api_key = "PMAK-694e3617a2ab760001fb150d-f135a271f9e745b6731cf6ab0d25b6bc7c"
    
    print(f"Initializing PostmanTool with key: {api_key[:10]}...")
    tool = PostmanTool(api_key=api_key)
    
    print("\n--- Testing list_workspaces ---")
    result = tool.execute("list_workspaces")
    print(f"Workspaces Result: {result}")

    print("\n--- Testing list_collections ---")
    result = tool.execute("list_collections")
    print(f"Collections Result: {result}")
    
    if result.get("success"):
        print("Successfully listed collections!")
        collections = result.get("collections", [])
        if collections:
            first = collections[0]
            cid = first['id']
            print(f"Found Collection ID: {cid} ({first.get('name')})")
            
            print(f"\n--- Testing get_collection {cid} ---")
            # This is a heavier call, just checking if it works
            details = tool.execute("get_collection", collection_id=cid)
            print(f"Get Collection Success: {details.get('success')}")
        else:
            print("No collections found.")
    else:
        print("Failed to list collections.")

if __name__ == "__main__":
    verify_postman()

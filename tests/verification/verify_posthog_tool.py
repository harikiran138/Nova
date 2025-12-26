import sys
import os
# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.nova_agents.tools.registry import ToolRegistry
from src.nova_agents.tools.posthog_tool import PostHogTool

def verify_posthog():
    # User provided key
    api_key = "phc_D0FHE7H0twyQLRZ7oO2hH1vu9RwwkvE3aR8TyBudUT0"
    
    print(f"Initializing PostHogTool with key: {api_key[:10]}...")
    tool = PostHogTool(api_key=api_key)
    
    print("\n--- Testing list_projects ---")
    # This might fail if it's a Project Key (phc_) instead of Personal Key (phx_)
    result = tool.execute("list_projects")
    print(f"Result: {result}")
    
    if result.get("success"):
        print("Successfully listed projects!")
        projects = result.get("projects", [])
        if projects:
            first_project = projects[0]
            pid = first_project['id']
            print(f"Found project ID: {pid}")
            
            print(f"\n--- Testing list_feature_flags for project {pid} ---")
            flags = tool.execute("list_feature_flags", project_id=pid)
            print(f"Flags: {flags}")
        else:
            print("No projects found.")
    else:
        print("Failed to list projects. Inspecting error...")
        if "401" in str(result) or "403" in str(result):
             print("\n[DIAGNOSIS] usage of 'phc_' key implies this is a Project API Key.")
             print("The Management API (listing projects etc) usually requires a Personal API Key (starts with 'phx_').")
             print("Please perform a check manually or asking user for a Personal API Key.")

if __name__ == "__main__":
    verify_posthog()

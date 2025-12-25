import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.nova_agents.tools.registry import ToolRegistry

def verify_tools():
    print("Initializing ToolRegistry...")
    registry = ToolRegistry()
    
    print("\nRegistered Tools:")
    tools = registry.list()
    for t in tools:
        print(f"- {t}")

    # Check Vision Tool
    if "vision.analyze" in tools:
        print("\n✅ VisionTool registered successfully.")
        vision = registry.get("vision.analyze")
        print(f"  Description: {vision.description}")
        print(f"  Model: {vision.model}")
    else:
        print("\n❌ VisionTool NOT registered.")

    # Check Browser Tool
    if "browser.browse" in tools:
        print("\n✅ BrowserTool registered successfully.")
        browser = registry.get("browser.browse")
        print(f"  Description: {browser.description}")
    else:
        print("\n❌ BrowserTool NOT registered (possibly due to missing dependencies).")

if __name__ == "__main__":
    verify_tools()

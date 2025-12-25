from pathlib import Path
from src.agent_core.tools.registry import ToolRegistry

registry = ToolRegistry(Path("."))
print("Tools loaded:", len(registry.tools))
print("Kali tools:", [t for t in registry.tools if "kali" in t])

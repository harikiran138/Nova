import importlib.util
import os
from pathlib import Path
from typing import List, Any

class PluginManager:
    """Manages loading of external plugins."""
    
    def __init__(self, plugin_dir: Path):
        self.plugin_dir = plugin_dir
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        
    def load_plugins(self, registry):
        """Load python scripts from plugin dir and register tools."""
        if not self.plugin_dir.exists(): return
        
        print(f"🔌 Loading plugins from {self.plugin_dir}...")
        for file in self.plugin_dir.glob("*.py"):
            try:
                spec = importlib.util.spec_from_file_location(file.stem, file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Look for 'tools' list in module
                if hasattr(module, "tools"):
                    for tool in module.tools:
                        if callable(tool):
                            # It's a function, use its name and docstring
                            registry.register(f"plugin.{tool.__name__}", tool)
                            print(f"  + Loaded: plugin.{tool.__name__}")
                        elif isinstance(tool, tuple) and len(tool) == 3:
                            # It's a tuple (name, func, desc)
                            registry.register(tool[0], tool[1], tool[2])
                            print(f"  + Loaded: {tool[0]}")
            except Exception as e:
                print(f"Failed to load plugin {file}: {e}")

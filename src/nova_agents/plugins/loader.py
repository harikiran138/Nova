"""
Plugin System for Nova - Enables dynamic tool loading.

Supports:
1. Loading tools from external Python packages
2. Discovering tools via entry points
3. Runtime registration of third-party tools
"""

import importlib
import importlib.util
from pathlib import Path
from typing import List, Dict, Any, Optional
import sys

from src.nova_agents.tools.base import Tool
from src.nova_agents.tools.registry import ToolRegistry


class PluginLoader:
    """
    Loads and manages external tool plugins.
    
    Plugins can be:
    1. Python files with Tool subclasses
    2. Packages with entry points
    3. Directories with tools/
    """
    
    def __init__(self, registry: ToolRegistry):
        """
        Initialize with a tool registry.
        
        Args:
            registry: ToolRegistry to register discovered tools
        """
        self.registry = registry
        self.loaded_plugins: Dict[str, List[str]] = {}  # plugin_name -> tool_names
    
    def load_from_file(self, file_path: str) -> List[str]:
        """
        Load tools from a Python file.
        
        Args:
            file_path: Path to Python file containing Tool subclasses
            
        Returns:
            List of tool names that were loaded
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Plugin file not found: {file_path}")
        
        # Load module
        spec = importlib.util.spec_from_file_location(path.stem, path)
        if not spec or not spec.loader:
            raise ImportError(f"Could not load {file_path}")
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[path.stem] = module
        spec.loader.exec_module(module)
        
        # Find Tool subclasses
        tools_loaded = []
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, Tool) and attr is not Tool:
                # Instantiate and register
                try:
                    tool_instance = attr()
                    self.registry.register(tool_instance)
                    tools_loaded.append(tool_instance.name)
                except Exception as e:
                    print(f"Failed to load tool {attr_name}: {e}")
        
        plugin_name = path.stem
        self.loaded_plugins[plugin_name] = tools_loaded
        return tools_loaded
    
    def load_from_directory(self, directory: str, pattern: str = "*.py") -> Dict[str, List[str]]:
        """
        Load all plugins from a directory.
        
        Args:
            directory: Path to directory containing plugin files
            pattern: Glob pattern for plugin files (default: *.py)
            
        Returns:
            Dict mapping plugin file names to loaded tool names
        """
        path = Path(directory)
        if not path.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory}")
        
        results = {}
        for plugin_file in path.glob(pattern):
            if plugin_file.stem.startswith("_"):
                continue  # Skip __init__.py and private files
            
            try:
                tools = self.load_from_file(str(plugin_file))
                results[plugin_file.stem] = tools
            except Exception as e:
                print(f"Failed to load plugin {plugin_file.name}: {e}")
        
        return results
    
    def load_from_package(self, package_name: str, entry_point: str = "nova_tools") -> List[str]:
        """
        Load tools from an installed package via entry points.
        
        Args:
            package_name: Name of the installed package
            entry_point: Entry point group name (default: 'nova_tools')
            
        Returns:
            List of tool names loaded
        """
        try:
            # Try to use importlib.metadata (Python 3.8+)
            from importlib.metadata import entry_points
            
            tools_loaded = []
            eps = entry_points()
            
            # Get entry points for this group
            if hasattr(eps, 'select'):  # Python 3.10+
                group = eps.select(group=entry_point)
            else:  # Python 3.8-3.9
                group = eps.get(entry_point, [])
            
            for ep in group:
                try:
                    tool_class = ep.load()
                    tool_instance = tool_class()
                    self.registry.register(tool_instance)
                    tools_loaded.append(tool_instance.name)
                except Exception as e:
                    print(f"Failed to load entry point {ep.name}: {e}")
            
            if tools_loaded:
                self.loaded_plugins[package_name] = tools_loaded
            
            return tools_loaded
            
        except ImportError:
            print("importlib.metadata not available (Python 3.8+ required)")
            return []
    
    def unload_plugin(self, plugin_name: str):
        """
        Unload a plugin (remove its tools from registry).
        
        Args:
            plugin_name: Name of the plugin to unload
        """
        if plugin_name not in self.loaded_plugins:
            return
        
        # Note: ToolRegistry doesn't have an unregister method yet
        # Would need to add that functionality
        print(f"Warning: Tool unloading not fully implemented. Plugin: {plugin_name}")
        del self.loaded_plugins[plugin_name]
    
    def list_plugins(self) -> Dict[str, List[str]]:
        """Get all loaded plugins and their tools."""
        return self.loaded_plugins.copy()

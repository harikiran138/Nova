import unittest
from pathlib import Path
from src.agent_core.tools.registry import ToolRegistry
from src.agent_core.tools.core_tools import FileTool, NetTool

class TestToolRegistryV2(unittest.TestCase):
    def setUp(self):
        self.workspace = Path("/tmp/nova_test_workspace")
        self.workspace.mkdir(exist_ok=True)
        self.registry = ToolRegistry(self.workspace, offline_mode=True)

    def test_offline_mode_propagation(self):
        print("\n--- Testing Offline Mode Propagation ---")
        self.assertTrue(self.registry.offline_mode)
        self.assertTrue(self.registry.net_tools_instance.offline_mode)
        print("✅ Offline mode propagated to NetTool")

    def test_file_tool_methods(self):
        print("\n--- Testing FileTool Methods ---")
        file_tool = self.registry.file_tools_instance
        self.assertTrue(hasattr(file_tool, 'delete'))
        self.assertTrue(hasattr(file_tool, 'copy'))
        print("✅ FileTool has delete and copy")

    def test_net_tool_methods(self):
        print("\n--- Testing NetTool Methods ---")
        net_tool = self.registry.net_tools_instance
        self.assertTrue(hasattr(net_tool, 'post'))
        self.assertTrue(hasattr(net_tool, 'get'))
        self.assertFalse(hasattr(net_tool, 'delete')) # Should NOT have delete
        print("✅ NetTool has post and NO delete")

    def test_registry_methods(self):
        print("\n--- Testing Registry Methods ---")
        self.assertTrue(hasattr(self.registry, '_load_plugins'))
        print("✅ Registry has _load_plugins")

if __name__ == "__main__":
    unittest.main()

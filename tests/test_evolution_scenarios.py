import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from src.agent_core.agent_loop import AgentLoop
from src.agent_core.tools.registry import ToolRegistry
from src.agent_core.model_client import OllamaClient
from src.agent_core.tasks import Task, TaskStep

class TestEvolutionScenarios(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock(spec=OllamaClient)
        self.mock_tools = MagicMock(spec=ToolRegistry)
        self.mock_tools.tools = {}
        self.loop = AgentLoop(self.mock_client, self.mock_tools)

    def test_scenario_rollback_on_failure(self):
        """Test that the loop rolls back if a tool step fails."""
        task = Task("T1", "Test task with failure")
        task.add_step("Fail this step", tool="fail_tool")
        
        # Mock tool failure
        self.mock_tools.execute.return_value = {"success": False, "error": "Simulated failure"}
        
        # Patch rollback manager
        with patch.object(self.loop.rollback_manager, 'create_checkpoint') as mock_cp, \
             patch.object(self.loop.rollback_manager, 'rollback') as mock_rb:
            
            result_task = self.loop.run_task(task)
            
            self.assertEqual(result_task.status, "failed")
            mock_cp.assert_called()
            mock_rb.assert_called()

    def test_scenario_self_healing_package(self):
        """Test that the loop attempts to install a package on ModuleNotFoundError."""
        error_msg = "ModuleNotFoundError: No module named 'scipy'"
        
        # Mock analyze_error to return the install action
        from src.agent_core.error_analysis import analyze_error
        
        with patch('src.agent_core.agent_loop.analyze_error') as mock_analyze:
            mock_analyze.return_value = {"action": "install_package", "target": "scipy"}
            
            # Mock installer tool in the registry
            self.mock_tools.installer_tools_instance = MagicMock()
            self.mock_tools.installer_tools_instance.execute.return_value = {"success": True}
            
            recovered = self.loop._handle_error_recovery("test_tool", {}, error_msg)
            self.assertTrue(recovered)
            self.mock_tools.installer_tools_instance.execute.assert_called_with({"package": "scipy"})

if __name__ == '__main__':
    unittest.main()

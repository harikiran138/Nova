import unittest
from unittest.mock import MagicMock
from src.agent_core.planner import Planner
from src.agent_core.tasks import Task

class TestPlannerRoles(unittest.TestCase):
    def test_plan_task_assigns_roles(self):
        print("\n--- Testing Planner Roles ---")
        
        # Mock Client
        client = MagicMock()
        client.generate.return_value = """
        {
            "steps": [
                {
                    "id": 1,
                    "description": "Research",
                    "tool": "net.search",
                    "args": {"query": "test"},
                    "role": "researcher"
                },
                {
                    "id": 2,
                    "description": "Code",
                    "tool": "file.write",
                    "args": {"file": "test.py"},
                    "role": "coder"
                }
            ]
        }
        """
        
        # Mock Tools
        mock_tool_1 = MagicMock()
        mock_tool_1.description = "Search tool"
        mock_tool_2 = MagicMock()
        mock_tool_2.description = "File tool"
        
        tools = MagicMock()
        tools.tools = {"net.search": mock_tool_1, "file.write": mock_tool_2}
        
        # Mock ToolSelector
        with unittest.mock.patch('src.agent_core.tool_selector.ToolSelector') as MockSelector:
            MockSelector.return_value.select_tools.return_value = ["net.search", "file.write"]
            
            planner = Planner(client, tools)
            task = planner.plan_task("Do something")
            
            print(f"Task Steps: {len(task.steps)}")
            self.assertEqual(len(task.steps), 2)
            
            step1 = task.steps[0]
            print(f"Step 1 Role: {step1.role}")
            self.assertEqual(step1.role, "researcher")
            
            step2 = task.steps[1]
            print(f"Step 2 Role: {step2.role}")
            self.assertEqual(step2.role, "coder")

if __name__ == "__main__":
    unittest.main()

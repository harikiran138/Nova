import unittest
from unittest.mock import MagicMock
from src.agent_core.planner import Planner
from src.agent_core.tasks import Task

class TestPlanner(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.mock_tools = MagicMock()
        self.mock_tools.get_tool_descriptions.return_value = "file.read - Read file"
        
        self.planner = Planner(self.mock_client, self.mock_tools)

    def test_plan_task_success(self):
        # Mock model response with valid JSON
        self.mock_client.generate.return_value = """
        ```json
        {
            "steps": [
                {"description": "Step 1", "tool": "file.read", "args": {"path": "test.txt"}}
            ]
        }
        ```
        """
        
        task = self.planner.plan_task("Read test.txt")
        
        self.assertEqual(task.goal, "Read test.txt")
        self.assertEqual(len(task.steps), 1)
        self.assertEqual(task.steps[0].description, "Step 1")
        self.assertEqual(task.steps[0].tool, "file.read")

    def test_plan_task_failure(self):
        # Mock model failure (None response)
        self.mock_client.generate.return_value = None
        
        task = self.planner.plan_task("Do something")
        
        self.assertEqual(len(task.steps), 1)
        self.assertIn("Analyze the goal", task.steps[0].description)

if __name__ == '__main__':
    unittest.main()

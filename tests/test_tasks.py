import unittest
from src.agent_core.tasks import Task, TaskStep

class TestTask(unittest.TestCase):
    def test_task_creation(self):
        task = Task(id="123", goal="Test Goal")
        self.assertEqual(task.id, "123")
        self.assertEqual(task.goal, "Test Goal")
        self.assertEqual(task.status, "pending")
        self.assertEqual(len(task.steps), 0)

    def test_add_step(self):
        task = Task(id="123", goal="Test Goal")
        task.add_step("Step 1", tool="file.read", args={"path": "test.txt"})
        
        self.assertEqual(len(task.steps), 1)
        step = task.steps[0]
        self.assertEqual(step.id, 1)
        self.assertEqual(step.description, "Step 1")
        self.assertEqual(step.tool, "file.read")
        self.assertEqual(step.args, {"path": "test.txt"})
        self.assertEqual(step.status, "pending")

    def test_json_serialization(self):
        task = Task(id="123", goal="Test Goal")
        task.add_step("Step 1")
        
        json_str = task.to_json()
        task2 = Task.from_json(json_str)
        
        self.assertEqual(task.id, task2.id)
        self.assertEqual(task.goal, task2.goal)
        self.assertEqual(len(task2.steps), 1)
        self.assertEqual(task2.steps[0].description, "Step 1")

if __name__ == '__main__':
    unittest.main()

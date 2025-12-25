import unittest
from unittest.mock import MagicMock
from pathlib import Path
from src.agent_core.agent_loop import AgentLoop
from src.agent_core.tools.registry import ToolRegistry

class TestHallucinationRecovery(unittest.TestCase):
    def setUp(self):
        self.workspace = Path("test_hallucination_ws")
        self.workspace.mkdir(exist_ok=True)
        self.registry = ToolRegistry(self.workspace)
        self.client = MagicMock()
        self.agent = AgentLoop(self.client, self.registry, profile_name="general", sandbox_mode=False)

    def test_recovery(self):
        print("\n--- Testing Hallucination Recovery ---")
        
        # Sequence of responses from the model:
        # 1. Hallucinated tool
        # 2. Correct tool (after seeing error)
        # 3. Final answer (None to stop loop)
        self.client.generate.side_effect = [
            '{"tool": "wikipedia", "args": {"query": "Tom Cruise"}}',
            '{"tool": "web.search", "args": {"query": "Tom Cruise"}}',
            "Tom Cruise is an actor."
        ]
        
        response = self.agent.process_input("Who is Tom Cruise?")
        
        # Check history
        # Turn 1: User input
        # Turn 2: Agent calls wikipedia
        # Turn 3: User (System) returns error with valid tools
        # Turn 4: Agent calls web.search
        # Turn 5: User (System) returns success
        # Turn 6: Agent responds
        
        history = self.agent.conversation_history
        
        # Verify Error Message contains valid tools
        error_msg = history[2]["content"]
        print(f"Error Message: {error_msg}")
        self.assertIn("Tool 'wikipedia' not found", error_msg)
        self.assertIn("Available tools:", error_msg)
        self.assertIn("web.search", error_msg)
        
        # Verify Recovery
        recovery_call = history[3]["content"]
        print(f"Recovery Call: {recovery_call}")
        self.assertIn("web.search", recovery_call)
        
        print("✅ Agent successfully recovered from hallucination.")

if __name__ == "__main__":
    unittest.main()

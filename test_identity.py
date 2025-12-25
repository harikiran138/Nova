import unittest
from unittest.mock import MagicMock
from src.agent_core.agent_loop import AgentLoop

class TestIdentity(unittest.TestCase):
    def test_system_prompt_enforces_nova_identity(self):
        print("\n--- Testing Identity Enforcement ---")
        
        # Check the static SYSTEM_PROMPT
        prompt = AgentLoop.SYSTEM_PROMPT
        
        print("Verifying 'I am Nova'...")
        self.assertIn("You are Nova — your local autonomous agent.", prompt)
        
        print("Verifying Identity Rules...")
        self.assertIn("IDENTITY & PRIVACY RULES", prompt)
        self.assertIn("You are \"Nova\". You are NOT a language model", prompt)
        
        print("Verifying Privacy Rules...")
        self.assertIn("You operate locally and privately", prompt)
        
        print("✅ Identity System Prompt Verified")

if __name__ == "__main__":
    unittest.main()

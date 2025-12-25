
import unittest
from unittest.mock import MagicMock, patch
import json
import requests
from src.nova_agents.agent_loop import AgentLoop
from src.nova_ai.model_client import OllamaClient

class TestFixes(unittest.TestCase):
    def setUp(self):
        self.mock_config = MagicMock()
        self.mock_config.workspace_dir = "/tmp"
        self.mock_config.debug_mode = True
        
    def test_trajectory_replay_integration(self):
        """Verify that past episodes are injected into the plan generation prompt."""
        # Setup AgentLoop with mocks
        agent = AgentLoop(self.mock_config, tools=[]) # Added tools=[]
        agent.memory = MagicMock()
        agent.client = MagicMock()
        
        # Mock Memory to return a relevant episode
        agent.memory.get_episodes.return_value = [{"steps": "Step 1: Do X. Step 2: Do Y."}]
        
        # Mock Client to capture the prompt and return a valid JSON response
        agent.client.generate.return_value = '{"plan": [{"step": 1, "description": "Test", "tool": "test", "confidence": 1.0}]}'
        
        # Execute
        agent.generate_plan("Test Goal")
        
        # Verify
        args, _ = agent.client.generate.call_args
        prompt = args[1]
        
        print(f"\nCaptured Prompt:\n{prompt[:200]}...") # Debug print
        
        self.assertIn("RELEVANT PAST EPISODES (Trajectory Replay):", prompt)
        self.assertIn("Step 1: Do X. Step 2: Do Y.", prompt)
        print("✅ Trajectory Replay verified.")

    def test_offline_streaming_fallback(self):
        """Verify that stream_generate yields an offline message on connection error."""
        client = OllamaClient(base_url="http://localhost:11434", model="test-model") # Added model argument
        
        # Mock requests.post to raise ConnectionError
        with patch('requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError("Failed to establish a new connection")
            
            # Execute
            generator = client.stream_generate("Test prompt")
            result = next(generator)
            
            # Verify
            print(f"\nYielded Result: {result}")
            self.assertIn("SYSTEM_OFFLINE", result)
            self.assertIn("Connection to neural engine lost", result)
            print("✅ Offline Streaming Fallback verified.")

if __name__ == '__main__':
    unittest.main()

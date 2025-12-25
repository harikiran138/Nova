import unittest
from unittest.mock import MagicMock, patch
from src.agent_core.config import Config
from src.nova_cli import handle_slash_command

class TestDynamicSwitching(unittest.TestCase):
    def setUp(self):
        self.config = Config.from_env()
        self.agent = MagicMock()
        self.client = MagicMock()
        self.client.model = "old-model"

    def test_provider_switch(self):
        print("\n--- Testing Provider Switch ---")
        action = handle_slash_command("/provider gemini", self.agent, self.client, self.config)
        self.assertEqual(action, "reload")
        self.assertEqual(self.config.model_provider, "gemini")
        print("✅ Switched to Gemini")
        
        action = handle_slash_command("/provider openrouter", self.agent, self.client, self.config)
        self.assertEqual(action, "reload")
        self.assertEqual(self.config.model_provider, "openrouter")
        print("✅ Switched to OpenRouter")

    @patch("src.nova_cli.select_model")
    def test_model_switch(self, mock_select):
        print("\n--- Testing Model Switch ---")
        mock_select.return_value = "new-model"
        
        # Test Gemini Model Switch
        self.config.model_provider = "gemini"
        action = handle_slash_command("/model", self.agent, self.client, self.config)
        self.assertEqual(action, "reload")
        self.assertEqual(self.config.gemini_model, "new-model")
        print("✅ Switched Gemini Model")

if __name__ == "__main__":
    unittest.main()

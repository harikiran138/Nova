import unittest
from unittest.mock import MagicMock, patch
from src.nova_cli import handle_slash_command, select_model
from src.agent_core import Config

class TestCliV2(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.mock_client.model = "llama3"
        self.mock_client.get_available_models.return_value = ["llama3", "qwen2"]
        
        self.mock_agent = MagicMock()
        self.mock_config = MagicMock()
        self.mock_config.ollama_model = "llama3"

    @patch("src.nova_cli.IntPrompt.ask")
    def test_select_model(self, mock_ask):
        # Simulate selecting the second model (qwen2)
        mock_ask.return_value = 2
        
        selected = select_model(self.mock_client, self.mock_config)
        self.assertEqual(selected, "qwen2")

    def test_slash_model(self):
        # We need to patch select_model since it's called by handle_slash_command
        with patch("src.nova_cli.select_model", return_value="qwen2") as mock_select:
            handle_slash_command("/model", self.mock_agent, self.mock_client, self.mock_config)
            
            self.assertEqual(self.mock_client.model, "qwen2")
            self.assertEqual(self.mock_config.ollama_model, "qwen2")

    def test_slash_clear(self):
        result = handle_slash_command("/clear", self.mock_agent, self.mock_client, self.mock_config)
        self.mock_agent.reset_conversation.assert_called_once()
        self.assertEqual(result, "continue")

    def test_slash_quit(self):
        result = handle_slash_command("/quit", self.mock_agent, self.mock_client, self.mock_config)
        self.assertEqual(result, "exit")

    def test_slash_unknown(self):
        result = handle_slash_command("/unknown", self.mock_agent, self.mock_client, self.mock_config)
        self.assertEqual(result, "continue")

if __name__ == '__main__':
    unittest.main()

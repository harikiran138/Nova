import os
import unittest
from unittest.mock import MagicMock, patch
from src.agent_core.config import Config
from src.agent_core.gemini_client import GeminiClient
from src.nova_cli import get_client

class TestGeminiIntegration(unittest.TestCase):
    def test_config_loading(self):
        print("\n--- Testing Config Loading ---")
        with patch.dict(os.environ, {"MODEL_PROVIDER": "gemini", "GEMINI_API_KEY": "fake_key"}):
            config = Config.from_env()
            self.assertEqual(config.model_provider, "gemini")
            self.assertEqual(config.gemini_api_key, "fake_key")
            print("✅ Config loaded correctly")

    def test_client_selection(self):
        print("\n--- Testing Client Selection ---")
        with patch.dict(os.environ, {"MODEL_PROVIDER": "gemini", "GEMINI_API_KEY": "fake_key"}):
            config = Config.from_env()
            client = get_client(config)
            self.assertIsInstance(client, GeminiClient)
            self.assertEqual(client.api_key, "fake_key")
            print("✅ get_client returned GeminiClient")

    @patch("requests.post")
    def test_gemini_generation(self, mock_post):
        print("\n--- Testing Gemini Generation ---")
        client = GeminiClient("fake_key")
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [
                {"content": {"parts": [{"text": "Hello from Gemini"}]}}
            ]
        }
        mock_post.return_value = mock_response
        
        response = client.generate([{"role": "user", "content": "Hi"}])
        print(f"Response: {response}")
        
        self.assertEqual(response, "Hello from Gemini")
        
        # Verify payload structure
        args, kwargs = mock_post.call_args
        payload = kwargs["json"]
        self.assertEqual(payload["contents"][0]["parts"][0]["text"], "Hi")
        print("✅ Payload structure verified")

if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import MagicMock, patch
from src.agent_core.tools.core_tools import NetTool

class TestPrivacyMode(unittest.TestCase):
    def test_offline_mode_blocks_access(self):
        print("\n--- Testing Offline Mode Block ---")
        net = NetTool(offline_mode=True)
        result = net.get("https://google.com")
        print(f"Result: {result}")
        self.assertIn("PERMISSION_DENIED", result)
        self.assertIn("Should I connect to the internet?", result)

    @patch("requests.Session")
    def test_online_mode_allows_access(self, mock_session):
        print("\n--- Testing Online Mode Access ---")
        net = NetTool(offline_mode=False)
        
        # Mock response
        mock_response = MagicMock()
        mock_response.text = "Success"
        mock_response.status_code = 200
        net.session.get.return_value = mock_response
        
        result = net.get("https://google.com")
        print(f"Result: {result}")
        self.assertEqual(result, "Success")

if __name__ == "__main__":
    unittest.main()

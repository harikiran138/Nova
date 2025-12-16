import unittest
import json
from unittest.mock import MagicMock, patch
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path.cwd() / "src"))

from agent_core.tools.registry import ToolRegistry
from agent_core.openrouter_client import OpenRouterClient
from agent_core.agent_loop import AgentLoop

class TestOpenRouterTools(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path.cwd() / "test_env"
        self.test_dir.mkdir(exist_ok=True)
        self.registry = ToolRegistry(self.test_dir)

    def test_schema_generation(self):
        print("\n[TEST] Schema Generation")
        defs = self.registry.tool_definitions
        self.assertTrue(len(defs) > 0)
        
        # Check file.write schema
        write_tool = next((t for t in defs if t["function"]["name"] == "file.write"), None)
        self.assertIsNotNone(write_tool)
        params = write_tool["function"]["parameters"]["properties"]
        self.assertIn("path", params)
        self.assertIn("content", params)
        print("✓ Schema generation successful")

    @patch("requests.post")
    def test_client_payload(self, mock_post):
        print("\n[TEST] OpenRouter Client Payload")
        client = OpenRouterClient("fake_key")
        tools = [{"type": "function", "function": {"name": "test"}}]
        
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "tool_calls": [{
                        "function": {
                            "name": "test",
                            "arguments": '{"arg": "val"}'
                        }
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response
        
        # Call generate
        response = client.generate([{"role": "user", "content": "hi"}], tools=tools)
        
        # Verify payload
        args, kwargs = mock_post.call_args
        payload = kwargs["json"]
        self.assertIn("tools", payload)
        self.assertEqual(payload["tools"], tools)
        self.assertEqual(payload["tool_choice"], "auto")
        
        # Verify response parsing
        parsed = json.loads(response)
        self.assertEqual(parsed["tool"], "test")
        self.assertEqual(parsed["args"]["arg"], "val")
        print("✓ Payload construction and response parsing successful")

if __name__ == "__main__":
    unittest.main()

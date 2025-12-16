import unittest
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
from src.agent_core.tools import ToolRegistry, parse_tool_call

class TestTools(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.workspace_dir = Path(self.test_dir).resolve()
        self.registry = ToolRegistry(
            workspace_dir=self.workspace_dir,
            allow_shell=True,
            shell_allowlist=["ls", "echo"]
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_file_write_and_read(self):
        # Test write
        write_args = {"path": "test.txt", "content": "Hello World"}
        result = self.registry.execute("file.write", write_args)
        self.assertTrue(result["success"], result.get("error"))
        self.assertTrue((self.workspace_dir / "test.txt").exists())

        # Test read
        read_args = {"path": "test.txt"}
        result = self.registry.execute("file.read", read_args)
        self.assertTrue(result["success"])
        self.assertEqual(result["result"], "Hello World")

    def test_file_security(self):
        # Test writing outside workspace
        result = self.registry.execute("file.write", {
            "path": "../outside.txt",
            "content": "hack"
        })
        self.assertFalse(result["success"])
        self.assertIn("must be within workspace", result["error"])

    def test_shell_run_allowed(self):
        result = self.registry.execute("shell.run", {"command": "echo 'hello'"})
        self.assertTrue(result["success"])
        self.assertIn("hello", result["result"])

    def test_shell_run_disallowed(self):
        result = self.registry.execute("shell.run", {"command": "whoami"})
        self.assertFalse(result["success"])
        self.assertIn("not in allowlist", result["error"])

    @patch("src.agent_core.tools.requests.get")
    def test_web_get(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = "<html><body>Test Content</body></html>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.registry.execute("web.get", {"url": "http://example.com"})
        self.assertTrue(result["success"])
        self.assertIn("Test Content", result["result"])

    def test_parse_tool_call(self):
        text = 'Some text {"tool": "file.read", "args": {"path": "test.txt"}} more text'
        result = parse_tool_call(text)
        self.assertEqual(result["tool"], "file.read")
        self.assertEqual(result["args"]["path"], "test.txt")

if __name__ == '__main__':
    unittest.main()

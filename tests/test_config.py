import unittest
import os
from pathlib import Path
from src.agent_core.config import Config

class TestConfig(unittest.TestCase):
    def setUp(self):
        # Save original env vars
        self.original_env = dict(os.environ)
        
    def tearDown(self):
        # Restore env vars
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_from_env_defaults(self):
        # Clear relevant env vars to test defaults
        if "OLLAMA_BASE_URL" in os.environ: del os.environ["OLLAMA_BASE_URL"]
        if "OLLAMA_MODEL" in os.environ: del os.environ["OLLAMA_MODEL"]
        if "WORKSPACE_DIR" in os.environ: del os.environ["WORKSPACE_DIR"]
        
        config = Config.from_env()
        
        self.assertEqual(config.ollama_base_url, "http://127.0.0.1:11434")
        self.assertEqual(config.ollama_model, "mannix/llama3.1-8b-abliterated")
        self.assertTrue(config.allow_shell_commands)
        self.assertTrue(config.workspace_dir.name, "workspace")

    def test_from_env_custom(self):
        os.environ["OLLAMA_BASE_URL"] = "http://test-url:11434"
        os.environ["OLLAMA_MODEL"] = "test-model"
        os.environ["ALLOW_SHELL_COMMANDS"] = "false"
        
        config = Config.from_env()
        
        self.assertEqual(config.ollama_base_url, "http://test-url:11434")
        self.assertEqual(config.ollama_model, "test-model")
        self.assertFalse(config.allow_shell_commands)

    def test_validate_valid(self):
        config = Config(
            ollama_base_url="http://localhost:11434",
            ollama_model="llama3",
            gemini_model="gemini-1.5-pro",
            ollama_embedding_model="all-minilm",
            model_provider="ollama",
            workspace_dir=Path("."),
            allow_shell_commands=True,
            shell_command_allowlist=[],
            mongodb_uri="mongodb://localhost:27017",
            mongodb_db_name="test_db",
            mongodb_collection_name="test_coll"
        )
        errors = config.validate()
        self.assertEqual(len(errors), 0)

        config = Config(
            ollama_base_url="invalid-url",
            ollama_model="llama3",
            gemini_model="gemini-1.5-pro",
            ollama_embedding_model="all-minilm",
            model_provider="ollama",
            workspace_dir=Path("."),
            allow_shell_commands=True,
            shell_command_allowlist=[],
            mongodb_uri="mongodb://localhost:27017",
            mongodb_db_name="test_db",
            mongodb_collection_name="test_coll"
        )
        errors = config.validate()
        self.assertEqual(len(errors), 1)
        self.assertIn("Invalid OLLAMA_BASE_URL", errors[0])

if __name__ == '__main__':
    unittest.main()

import sys
import os
import shutil
import time
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.append(str(Path.cwd() / "src"))

from agent_core.config import Config
from agent_core.autonomy import ErrorPredictor, IntentModel
from agent_core.multi_agent import MultiAgentManager
from agent_core.offline_docs import OfflineDocs
from agent_core.knowledge_base import analyze_error
from agent_core.safety import SafetyPolicy, SafetyLevel
from agent_core.memory import MemoryManager
from agent_core.vector_store import VectorStore
from agent_core.telemetry import TelemetryManager
from agent_core.tools.registry import ToolRegistry
from agent_core.agent_loop import AgentLoop

class TestNovaV3(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = Path.cwd() / "test_env"
        self.test_dir.mkdir(exist_ok=True)
        self.config = Config.from_env()
        self.config.workspace_dir = self.test_dir
        
    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_performance_async(self):
        print("\n[TEST] Performance: Async Execution & Pruning")
        # Mock tools
        registry = ToolRegistry(self.test_dir)
        registry.register("test.tool", lambda x: {"success": True, "result": "ok"}, "Test Tool")
        
        agent = AgentLoop(None, registry, sandbox_mode=False)
        agent.config = self.config
        
        # Test Pruning
        agent.conversation_history = [{"role": "user", "content": f"msg {i}"} for i in range(25)]
        agent._prune_context()
        self.assertLessEqual(len(agent.conversation_history), 21) # 20 + system prompt implicit? No, list is explicit.
        print("✓ Context Pruning working")

    def test_autonomy(self):
        print("\n[TEST] Autonomy: Error Prediction & Intent")
        predictor = ErrorPredictor()
        risk = predictor.check_risk("rm -rf /")
        self.assertIsNotNone(risk)
        print(f"✓ Error Prediction caught risk: {risk}")
        
        intent = IntentModel()
        next_action = intent.predict_next("git add .")
        self.assertEqual(next_action, "git commit")
        print(f"✓ Intent Model predicted: {next_action}")

    def test_multi_agent(self):
        print("\n[TEST] Multi-Agent System")
        registry = ToolRegistry(self.test_dir)
        manager = MultiAgentManager(registry)
        
        role = manager.dispatch("scan for vulnerabilities")
        self.assertEqual(role, "security")
        
        role = manager.dispatch("refactor this function")
        self.assertEqual(role, "coder")
        
        agent = manager.get_agent("security")
        self.assertTrue(agent.sandbox_mode)
        print("✓ Dispatcher and Agent Factory working")

    def test_offline_intelligence(self):
        print("\n[TEST] Offline Intelligence")
        docs = OfflineDocs()
        # Mock subprocess run to avoid actual man page calls
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = "GIT(1) Git Manual"
            doc = docs.get_doc("git")
            self.assertIn("GIT(1)", doc)
            
        fix = analyze_error("fatal: not a git repository")
        self.assertEqual(fix['type'], "git_error")
        print("✓ Offline Docs and Knowledge Base working")

    def test_security(self):
        print("\n[TEST] Security: Encryption & Zero-Trust")
        # Encryption
        mem_dir = self.test_dir / "memory"
        mem = MemoryManager(mem_dir)
        data = {"secret": "nova_v3"}
        mem._save_json("test_enc.json", data)
        
        # Verify file is encrypted (not plain json)
        with open(mem_dir / "test_enc.json", "rb") as f:
            content = f.read()
            self.assertFalse(b"nova_v3" in content)
            
        loaded = mem._load_json("test_enc.json")
        self.assertEqual(loaded["secret"], "nova_v3")
        print("✓ Memory Encryption working")
        
        # Zero Trust
        safety = SafetyPolicy(SafetyLevel.RESTRICTED, self.test_dir, security_mode=True)
        allowed, reason = safety.check_tool_permission("file.delete", {"path": "test.txt"})
        self.assertFalse(allowed)
        
        token = safety.token_manager.generate_token("file.delete")
        allowed, reason = safety.check_tool_permission("file.delete", {"path": "test.txt"}, token=token)
        self.assertTrue(allowed)
        print("✓ Zero-Trust and Token Validation working")

    def test_memory_vector(self):
        print("\n[TEST] Memory: Vector Store")
        store = VectorStore(self.test_dir / "vectors.json")
        
        # Mock embedding
        with patch.object(store, "_get_embedding", return_value=[0.1, 0.2, 0.3]):
            store.add("hello world")
            results = store.search("hello")
            self.assertEqual(len(results), 1)
        print("✓ Vector Store working")

    def test_telemetry(self):
        print("\n[TEST] Telemetry")
        tm = TelemetryManager(self.test_dir / "telemetry.json")
        tm.log_task(True, 100)
        stats = tm.get_stats()
        self.assertEqual(stats["total_tasks"], 1)
        print("✓ Telemetry logging working")

if __name__ == "__main__":
    unittest.main()

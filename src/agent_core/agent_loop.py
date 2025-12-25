# Re-export AgentLoop and provide placeholder names for patch points in tests
from src.nova_agents.agent_loop import AgentLoop as _AgentLoop

# Patch points used in tests (allow mocking even if not used directly)
try:
    from src.nova_ops.error_analysis import analyze_error
except Exception:
    def analyze_error(*args, **kwargs):
        return "", []

# Dummy placeholders to allow unittest.mock.patch on these symbols
class KnowledgeStore: pass
class LearningAgent: pass
class SafetyPolicy: pass

AgentLoop = _AgentLoop
__all__ = ["AgentLoop", "analyze_error", "KnowledgeStore", "LearningAgent", "SafetyPolicy"]

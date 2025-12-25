import pytest
from pathlib import Path
from src.nova_ai.memory import MemoryManager

def test_memory_manager_tiering(tmp_path):
    """Test that MemoryManager supports tiered storage (Short, Long, Episodic)."""
    memory_dir = tmp_path / "memory"
    memory_manager = MemoryManager(memory_dir)
    
    # 1. Short-term (Session) - Already exists, but let's verify
    session_id = "test_session"
    history = [{"role": "user", "content": "hello"}]
    memory_manager.save_session(session_id, history)
    session = memory_manager.load_session(session_id)
    assert session.id == session_id
    assert session.history == history
    
    # 2. Long-term (Facts/RAG) - Already exists
    fact = "The capital of France is Paris."
    memory_manager.add_fact(fact)
    assert fact in memory_manager.get_facts()
    
    # 3. Episodic Memory (New requirement)
    episode = {
        "task": "write_flask_app",
        "success": True,
        "pattern": "Import Flask, create app, define route, run app."
    }
    memory_manager.save_episode(episode)
    episodes = memory_manager.get_episodes(task="write_flask_app")
    assert len(episodes) > 0
    assert episodes[0]["pattern"] == episode["pattern"]


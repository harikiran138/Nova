import pytest
import time
from pathlib import Path
from src.agent_core.memory import MemoryManager

@pytest.fixture
def temp_memory_dir(tmp_path):
    return tmp_path / "memory"

def test_save_and_load_session(temp_memory_dir):
    manager = MemoryManager(temp_memory_dir)
    session_id = "test_session_1"
    history = [{"role": "user", "content": "Hello"}]
    metadata = {"profile": "general"}
    
    # Save
    manager.save_session(session_id, history, metadata)
    
    # Load
    session = manager.load_session(session_id)
    assert session is not None
    assert session.id == session_id
    assert session.history == history
    assert session.metadata == metadata
    assert session.timestamp > 0

def test_list_sessions(temp_memory_dir):
    manager = MemoryManager(temp_memory_dir)
    
    # Create two sessions
    manager.save_session("s1", [{"role": "user", "content": "Hi 1"}])
    time.sleep(0.1) # Ensure timestamp diff
    manager.save_session("s2", [{"role": "user", "content": "Hi 2"}])
    
    sessions = manager.list_sessions()
    assert len(sessions) == 2
    
    ids = [s["id"] for s in sessions]
    assert "s1" in ids
    assert "s2" in ids
    
    # Check preview
    s1 = next(s for s in sessions if s["id"] == "s1")
    assert s1["preview"] == "Hi 1"

def test_load_nonexistent_session(temp_memory_dir):
    manager = MemoryManager(temp_memory_dir)
    session = manager.load_session("fake_id")
    assert session is None

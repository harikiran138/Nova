import json
import pytest
from pathlib import Path
from src.agent_core.learning.trajectory import TrajectoryLogger

def test_trajectory_logging(tmp_path):
    """Test that TrajectoryLogger logs steps and saves to file."""
    logger = TrajectoryLogger(tmp_path)
    
    logger.log_step("input", {"content": "Hello"})
    logger.log_step("thought", {"content": "I should respond"})
    logger.log_step("response", {"content": "Hi there!"})
    
    file_path = logger.finalize(success=True, metadata={"user": "test_user"})
    
    assert file_path.exists()
    
    with open(file_path, "r") as f:
        data = json.load(f)
        
    assert data["success"] is True
    assert data["metadata"]["user"] == "test_user"
    assert len(data["steps"]) == 3
    assert data["steps"][0]["type"] == "input"
    assert data["steps"][1]["data"]["content"] == "I should respond"

def test_trajectory_logger_reset(tmp_path):
    """Test that logger resets after finalize."""
    logger = TrajectoryLogger(tmp_path)
    logger.log_step("input", {"content": "Test"})
    logger.finalize(success=True)
    
    assert len(logger.current_trajectory) == 0
    assert logger.session_id.startswith("traj_")

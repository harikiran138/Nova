import pytest
from src.nova_backend.tasks.state_machine import StateMachine, TaskState
from src.nova_backend.tasks.tasks import Task

def test_valid_transitions():
    """Test standard happy path transitions."""
    assert StateMachine.transition("pending", "in_progress") == "in_progress"
    assert StateMachine.transition("in_progress", "completed") == "completed"
    assert StateMachine.transition("in_progress", "failed") == "failed"
    assert StateMachine.transition("failed", "pending") == "pending"

def test_invalid_transitions():
    """Test transitions that should be blocked."""
    with pytest.raises(ValueError):
        StateMachine.transition("failed", "completed") # Can't just complete a filed task without retrying
    
    with pytest.raises(ValueError):
        StateMachine.transition("pending", "completed") # Must start first
        
    with pytest.raises(ValueError):
        StateMachine.transition("completed", "failed") # Can't fail after success

def test_task_integration():
    """Test Task class integration."""
    t = Task(id="1", goal="Test")
    assert t.status == "pending"
    
    t.transition_to("in_progress")
    assert t.status == "in_progress"
    
    t.transition_to("completed")
    assert t.status == "completed"
    
    with pytest.raises(ValueError):
        t.transition_to("failed")

from enum import Enum
from typing import Dict, List, Set, Optional

class TaskState(Enum):
    PENDING = "pending"
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"

class StateMachine:
    """
    Enforces valid state transitions for Tasks and TaskSteps.
    """
    
    # Define valid transitions
    TRANSITIONS: Dict[TaskState, Set[TaskState]] = {
        TaskState.PENDING: {TaskState.PLANNING, TaskState.IN_PROGRESS, TaskState.SKIPPED, TaskState.FAILED},
        TaskState.PLANNING: {TaskState.IN_PROGRESS, TaskState.FAILED},
        TaskState.IN_PROGRESS: {TaskState.COMPLETED, TaskState.FAILED, TaskState.BLOCKED, TaskState.SKIPPED},
        TaskState.BLOCKED: {TaskState.IN_PROGRESS, TaskState.FAILED},
        TaskState.FAILED: {TaskState.PENDING, TaskState.IN_PROGRESS}, # Allow retry
        TaskState.COMPLETED: {TaskState.IN_PROGRESS}, # Allow re-opening if needed (rare)
        TaskState.SKIPPED: {TaskState.PENDING} # Allow reset
    }

    @staticmethod
    def validate_transition(current_state: TaskState, new_state: TaskState) -> bool:
        """Check if a transition is valid."""
        if current_state == new_state:
            return True
            
        allowed = StateMachine.TRANSITIONS.get(current_state, set())
        if new_state in allowed:
            return True
        return False

    @staticmethod
    def transition(current_state_str: str, new_state_str: str) -> str:
        """
        Attempt to transition from current state to new state.
        Raises ValueError if invalid.
        Returns the new state string.
        """
        try:
            curr = TaskState(current_state_str)
            new_s = TaskState(new_state_str)
        except ValueError:
             raise ValueError(f"Invalid state string: {current_state_str} or {new_state_str}")

        if StateMachine.validate_transition(curr, new_s):
            return new_s.value
        
        raise ValueError(f"Invalid transition from {curr.value} to {new_s.value}")

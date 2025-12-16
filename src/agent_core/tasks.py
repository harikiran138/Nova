from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path

@dataclass
class TaskStep:
    id: int
    description: str
    tool: Optional[str] = None
    args: Optional[Dict[str, Any]] = None
    role: str = "general" # supervisor, coder, researcher, reviewer
    status: str = "pending"  # pending, in_progress, completed, failed, skipped
    result: Optional[str] = None
    error: Optional[str] = None

@dataclass
class Task:
    id: str
    goal: str
    steps: List[TaskStep] = field(default_factory=list)
    status: str = "pending"  # pending, planning, in_progress, completed, failed
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    history: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Task':
        data = json.loads(json_str)
        steps_data = data.pop('steps', [])
        task = cls(**data)
        task.steps = [TaskStep(**step) for step in steps_data]
        return task

    def add_step(self, description: str, tool: Optional[str] = None, args: Optional[Dict[str, Any]] = None, role: str = "general"):
        step_id = len(self.steps) + 1
        self.steps.append(TaskStep(id=step_id, description=description, tool=tool, args=args, role=role))

    def get_next_pending_step(self) -> Optional[TaskStep]:
        for step in self.steps:
            if step.status == "pending":
                return step
        return None

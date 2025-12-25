import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

class TrajectoryLogger:
    """Logs agent interaction trajectories for training data collection."""
    
    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_trajectory: List[Dict[str, Any]] = []
        self.session_id: str = f"traj_{int(time.time())}"
        
    def log_step(self, step_type: str, data: Dict[str, Any]):
        """Log a single step in the trajectory."""
        entry = {
            "timestamp": time.time(),
            "type": step_type,
            "data": data
        }
        self.current_trajectory.append(entry)
        
    def finalize(self, success: bool, metadata: Optional[Dict[str, Any]] = None):
        """Save the trajectory to a file."""
        if not self.current_trajectory:
            return
            
        payload = {
            "session_id": self.session_id,
            "success": success,
            "metadata": metadata or {},
            "steps": self.current_trajectory
        }
        
        file_path = self.log_dir / f"{self.session_id}.json"
        with open(file_path, "w") as f:
            json.dump(payload, f, indent=2)
            
        self.current_trajectory = []
        self.session_id = f"traj_{int(time.time())}"
        return file_path

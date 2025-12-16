import time
import json
from pathlib import Path
from typing import Dict, Any

class PerformanceMonitor:
    """Tracks execution metrics for tools and LLM calls."""
    
    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
    def log_event(self, event_type: str, name: str, duration_ms: float, metadata: Dict[str, Any] = None):
        """Log a performance event."""
        entry = {
            "timestamp": time.time(),
            "type": event_type,
            "name": name,
            "duration_ms": duration_ms,
            "metadata": metadata or {}
        }
        
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def start_timer(self) -> float:
        return time.perf_counter()
        
    def stop_timer(self, start_time: float) -> float:
        return (time.perf_counter() - start_time) * 1000

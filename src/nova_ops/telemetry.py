import json
import time
from pathlib import Path
from typing import Dict

class TelemetryManager:
    """Tracks agent performance metrics."""
    
    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.metrics = self._load()

    def log_task(self, success: bool, duration_ms: float):
        """Log a task completion."""
        self.metrics["total_tasks"] += 1
        if success:
            self.metrics["successful_tasks"] += 1
        self.metrics["last_updated"] = time.time()
        self._save()

    def log_tokens(self, prompt: int, completion: int):
        self.metrics["prompt_tokens"] = self.metrics.get("prompt_tokens", 0) + prompt
        self.metrics["completion_tokens"] = self.metrics.get("completion_tokens", 0) + completion
        self.metrics["total_tokens"] = self.metrics.get("total_tokens", 0) + prompt + completion
        self._save()

    def log_cost(self, amount: float):
        """Log estimated cost in USD."""
        self.metrics["total_cost"] = self.metrics.get("total_cost", 0.0) + amount
        self._save()

    def log_cache(self, hit: bool):
        if hit:
            self.metrics["cache_hits"] = self.metrics.get("cache_hits", 0) + 1
        else:
            self.metrics["cache_misses"] = self.metrics.get("cache_misses", 0) + 1
        self._save()

    def get_stats(self) -> Dict:
        """Get current statistics."""
        total = self.metrics["total_tasks"]
        success = self.metrics["successful_tasks"]
        rate = (success / total * 100) if total > 0 else 0.0
        avg_duration = (self.metrics["total_duration_ms"] / total) if total > 0 else 0.0
        
        return {
            "success_rate": f"{rate:.1f}%",
            "total_tasks": total,
            "avg_duration": f"{avg_duration:.0f}ms",
            "tokens": {
                "total": self.metrics.get("total_tokens", 0),
                "prompt": self.metrics.get("prompt_tokens", 0),
                "completion": self.metrics.get("completion_tokens", 0)
            },
            "cost": f"${self.metrics.get('total_cost', 0.0):.4f}",
            "cache": {
                "hits": self.metrics.get("cache_hits", 0),
                "misses": self.metrics.get("cache_misses", 0)
            }
        }

    def _load(self) -> Dict:
        if self.log_path.exists():
            try:
                return json.loads(self.log_path.read_text())
            except:
                pass
        return {
            "total_tasks": 0,
            "successful_tasks": 0,
            "total_duration_ms": 0.0,
            "last_updated": 0.0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }

    def _save(self):
        self.log_path.write_text(json.dumps(self.metrics))

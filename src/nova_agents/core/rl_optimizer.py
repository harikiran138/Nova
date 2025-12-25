import json
import random
import math
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

class SearchBackendOptimizer:
    """
    Reinforcement Learning (Multi-Armed Bandit) optimizer for selecting
    the most reliable search backend.
    
    Uses Epsilon-Greedy strategy to balance:
    - Exploitation: Using the best known backend
    - Exploration: Occasionally trying other backends to see if they recovered
    """
    
    def __init__(self, data_dir: str = ".nova_cache", epsilon: float = 0.15):
        self.data_dir = Path(data_dir)
        self.state_file = self.data_dir / "search_rl_state.json"
        self.epsilon = epsilon  # Exploration rate (15% chance to explore)
        
        # Available arms (backends)
        self.backends = ["lite", "html", "api", "scrape", "wiki", "arxiv"]
        
        # Q-values: Expected reward for each backend (0.0 to 1.0)
        # Initialize optimistically to encourage trying everything at least once
        self.q_values = {b: 0.8 for b in self.backends}
        
        # Count of times each backend has been chosen
        self.counts = {b: 0 for b in self.backends}
        
        self._load_state()
        
    def select_backend(self, excluded: List[str] = None) -> str:
        """Select a backend to use."""
        excluded = excluded or []
        available = [b for b in self.backends if b not in excluded]
        
        if not available:
            return "lite"  # Fallback valid option
            
        # Exploration: Randomly select an arm
        if random.random() < self.epsilon:
            return random.choice(available)
            
        # Exploitation: Select arm with highest Q-value
        # Add tiny random noise to break ties
        return max(available, key=lambda b: self.q_values.get(b, 0) + random.uniform(0, 0.01))
        
    def update(self, backend: str, reward: float):
        """
        Update Q-value for the chosen backend based on reward.
        Reward: 1.0 (Success), -1.0 (Hard Limit), -0.5 (Empty/Soft Fail)
        """
        if backend not in self.q_values:
            return
            
        self.counts[backend] += 1
        n = self.counts[backend]
        
        # Running average update: NewQ = OldQ + (Reward - OldQ) / N
        # We use a learning rate (alpha) instead of 1/N to allow non-stationary tracking
        # (i.e., adapting when a backend goes down or comes back up)
        alpha = 0.2  # Learning rate
        
        old_q = self.q_values[backend]
        new_q = old_q + alpha * (reward - old_q)
        
        # Clamp Q-values
        self.q_values[backend] = max(-1.0, min(1.0, new_q))
        
        self._save_state()
        
    def _load_state(self):
        """Load RL state from disk."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.q_values.update(data.get("q_values", {}))
                    self.counts.update(data.get("counts", {}))
            except Exception:
                pass  # Start fresh on corruption
                
    def _save_state(self):
        """Save RL state to disk."""
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "q_values": self.q_values,
                    "counts": self.counts
                }, f)
        except Exception:
            pass

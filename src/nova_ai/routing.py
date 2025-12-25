from typing import Dict, Optional
from enum import Enum
import time

class ModelTier(Enum):
    FAST = "fast"         # e.g., llama3-8b, gemma-7b (Cheap, Fast)
    BALANCED = "balanced" # e.g., mixtral, llama3-70b (Medium)
    POWERFUL = "powerful" # e.g., gpt-4, claude-3-opus (Expensive, Slow)

class BudgetManager:
    """Tracks token usage and estimated cost."""
    
    # Generic cost per 1k tokens (USD-like units for estimation)
    COSTS = {
        ModelTier.FAST: 0.0001,
        ModelTier.BALANCED: 0.0005,
        ModelTier.POWERFUL: 0.002
    }

    def __init__(self, daily_budget: float = 1.0):
        self.daily_budget = daily_budget
        self.current_spend = 0.0
        self.token_usage = {tier: 0 for tier in ModelTier}
        self.start_time = time.time()

    def track(self, tier: ModelTier, tokens: int):
        cost = tokens * self.COSTS[tier] / 1000
        self.current_spend += cost
        self.token_usage[tier] += tokens

    def remaining_budget(self) -> float:
        return max(0, self.daily_budget - self.current_spend)

    def can_afford(self, tier: ModelTier, estimated_tokens: int = 1000) -> bool:
        cost = estimated_tokens * self.COSTS[tier] / 1000
        return self.remaining_budget() >= cost

class ModelRouter:
    """Selects the best model based on query complexity and budget."""
    
    def __init__(self, budget_manager: BudgetManager):
        self.budget = budget_manager

    def route(self, query: str, active_models: Dict[str, str]) -> str:
        """
        Returns the model_name to use.
        active_models: Dict mapping Tier to specific model name.
        """
        complexity = self._assess_complexity(query)
        
        # Default strategy: Use lowest efficient tier that fits budget
        if complexity == ModelTier.POWERFUL:
            if self.budget.can_afford(ModelTier.POWERFUL):
                return active_models.get(ModelTier.POWERFUL.value, active_models.get(ModelTier.BALANCED.value))
        
        if complexity == ModelTier.BALANCED:
            if self.budget.can_afford(ModelTier.BALANCED):
                 return active_models.get(ModelTier.BALANCED.value, active_models.get(ModelTier.FAST.value))
                 
        return active_models.get(ModelTier.FAST.value, "default_model")

    def _assess_complexity(self, query: str) -> ModelTier:
        """Heuristic complexity assessment."""
        # Simple heuristics for now
        length = len(query)
        keywords = ["code", "design", "architecture", "plan", "complex", "refactor", "debug"]
        
        if length > 2000 or query.count('\n') > 50:
            return ModelTier.POWERFUL
            
        if any(k in query.lower() for k in keywords):
             return ModelTier.BALANCED
             
        return ModelTier.FAST

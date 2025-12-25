import pytest
from src.nova_ai.routing import ModelRouter, BudgetManager, ModelTier

def test_model_router_heuristics():
    budget = BudgetManager(daily_budget=1.0)
    router = ModelRouter(budget)
    
    models = {
        "fast": "gemma:2b",
        "balanced": "llama3",
        "powerful": "llama3:70b"
    }
    
    # 1. Simple query -> Fast model
    tier, model = router.route("Hello world", models)
    assert model == "gemma:2b"
    assert tier.value == "fast"
    
    # 2. Coding query -> Balanced model
    tier, model = router.route("Write a python script to sort a list", models)
    assert model == "llama3"
    
    # 3. Complex/Long query -> Powerful model
    long_query = "Refactor this architecture: " + ("abc " * 1000)
    tier, model = router.route(long_query, models)
    assert model == "llama3:70b"

def test_budget_restriction():
    # Tiny budget
    budget = BudgetManager(daily_budget=0.00001)
    router = ModelRouter(budget)
    
    models = {
        "fast": "gemma:2b",
        "balanced": "llama3",
        "powerful": "llama3:70b"
    }
    
    # Even if complex, should fall back to fast because budget is gone
    # (assuming we use can_afford check)
    # The current implementation falls back if can_afford returns False
    tier, model = router.route("Extremely complex task", models)
    assert model == "gemma:2b"
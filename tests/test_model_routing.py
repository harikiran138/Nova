import pytest
import time
from src.nova_ai.routing import ModelRouter, BudgetManager, ModelTier

def test_budget_tracking():
    bm = BudgetManager(daily_budget=0.01)
    bm.track(ModelTier.FAST, 1000) # 0.0001
    assert bm.current_spend == 0.0001
    
    bm.track(ModelTier.POWERFUL, 1000) # 0.002
    assert bm.current_spend == 0.0021

def test_routing_logic_simple():
    bm = BudgetManager(daily_budget=1.0)
    router = ModelRouter(bm)
    
    active_models = {
        "fast": "fast_model",
        "balanced": "balanced_model",
        "powerful": "powerful_model"
    }
    
    # Simple query -> Fast model
    # Note: Our simple heuristic uses length < 2000 and no complex keywords
    query = "Hello, how are you?"
    model = router.route(query, active_models)
    assert model == "fast_model"

def test_routing_logic_complex():
    bm = BudgetManager(daily_budget=1.0)
    router = ModelRouter(bm)
    
    active_models = {
        "fast": "fast_model",
        "balanced": "balanced_model",
        "powerful": "powerful_model"
    }
    
    # Complex keyword -> Balanced model
    query = "Can you design a software architecture for me?"
    model = router.route(query, active_models)
    assert model == "balanced_model"
    
def test_budget_constraint_downgrade():
    bm = BudgetManager(daily_budget=0.00001) # Very low budget
    # Exhaust budget immediately
    bm.track(ModelTier.POWERFUL, 10000) 
    
    router = ModelRouter(bm)
    active_models = {
        "fast": "fast_model",
        "balanced": "balanced_model",
        "powerful": "powerful_model"
    }
    
    # Even for complex query, should downgrade if possible or stay lowest
    # Actually logic says: if complexity=POWERFUL, check budget. If no budget, fall through.
    # If falling through, it eventually returns fast or default.
    query = "Super complex code refactoring task that is very long " * 100
    model = router.route(query, active_models)
    
    # Since budget is blown, it should NOT return powerful_model
    assert model != "powerful_model"

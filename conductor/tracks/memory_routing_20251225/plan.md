# Track Plan: Advanced Memory & Dynamic Routing

## Phase 1: Tiered Memory Architecture
- [ ] Task: Create `MemoryManager` class with Short-term, Long-term, and Episodic stores.
- [ ] Task: Integrate ChromaDB for Long-term vector storage.
- [ ] Task: Implement `EpisodicStore` to save successful task patterns.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Tiered Memory Architecture' (Protocol in workflow.md)

## Phase 2: Dynamic Model Routing
- [ ] Task: Create `ModelRouter` class with complexity analysis logic.
- [ ] Task: Implement `BudgetManager` to track and limit token usage/cost.
- [ ] Task: Update `AgentLoop` to use `ModelRouter` for model selection.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Dynamic Model Routing' (Protocol in workflow.md)

## Phase 3: Context Optimization
- [ ] Task: Implement `ContextCompressor` to summarize old conversation history.
- [ ] Task: Add automatic pruning triggers to the Agent Loop.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Context Optimization' (Protocol in workflow.md)

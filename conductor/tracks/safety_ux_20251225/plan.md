# Track Plan: Industrial Safety & UX Hardening

## Phase 1: Explicit System States
- [ ] Task: Create `SystemState` enum and `HealthMonitor` class in `nova_ops/safety.py`.
- [ ] Task: Integrate `HealthMonitor` into `AgentLoop` to track failures.
- [ ] Task: Implement the "HALT Protocol" (freeze execution on critical failure).
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Explicit System States' (Protocol in workflow.md)

## Phase 2: Dry-Run & Simulation
- [ ] Task: Add `dry_run` parameter to `FileTool` and `ShellTool`.
- [ ] Task: Implement "Shadow Execution" logic (logging intent instead of acting).
- [ ] Task: Enforce Dry-Run if confidence score is < 0.8 during planning.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Dry-Run & Simulation' (Protocol in workflow.md)

## Phase 3: Cyberpunk TUI Evolution
- [ ] Task: Create `PlanTreeWidget` using `rich.tree` for the TUI.
- [ ] Task: Implement `ReasoningPanel` to show "Thought/Reflection" logs.
- [ ] Task: Integrate real-time latency and token metrics into the TUI header.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Cyberpunk TUI Evolution' (Protocol in workflow.md)

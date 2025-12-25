# Product Guidelines: Nova Industrial Standards

## 1. Safety & Autonomy Gates
*   **Circuit Breakers:** Implement mandatory resource and time limits for all autonomous loops. If a loop exceeds the threshold, the agent must enter a `HALT` state.
*   **Dry-Run Simulation:** All destructive operations (file deletions, system changes) must support a dry-run mode. The agent should default to dry-run when confidence is low.
*   **User Approval Gates:** High-risk actions (e.g., executing shell scripts, modifying `.env` files) require explicit user confirmation.

## 2. Intelligence & Reasoning Standards
*   **Plan Validation:** Every mission must start with a planning phase. The plan must be validated against the project spec before the first action is taken.
*   **Self-Critique:** The agent must perform a self-reflection step after every major phase to verify output quality and path efficiency.
*   **Failure States:** System must explicitly report its health state: `SAFE`, `WARNING`, `DEGRADED`, or `HALT`.

## 3. Engineering & Quality
*   **Testing:** Target 80%+ code coverage. New tools must include integration tests that simulate both success and failure scenarios.
*   **Local-First Integrity:** No features shall be implemented that require external API calls or telemetry without explicit user opt-in.
*   **Regression Detection:** Use saved trajectories to run regression suites, ensuring that intelligence upgrades do not break existing tool capabilities.

## 4. Documentation & UX
*   **The "Explain-Why" Principle:** Every autonomous decision must be logged with a clear rationale.
*   **Cyberpunk Aesthetic:** Maintain the neon-themed TUI consistency. Visual feedback (e.g., plan trees) must be real-time and readable.

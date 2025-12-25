# Project Workflow: Nova

## 1. Development Process
*   **Test-Driven Development (TDD):** Write tests before implementing features or fixing bugs.
*   **Task-Based Work:** All work is organized into tasks within a track's `plan.md`.
*   **Commits:** Commit changes after every completed task.

## 2. Quality Gates
*   **Test Coverage:** Maintain a minimum of **80%** code coverage.
*   **Linting & Types:** All code must pass linting and type checking (e.g., `ruff`, `tsc`) before completion.

## 3. Documentation & Checkpointing
*   **Task Summaries:** Use **Git Notes** to record a summary of what was done in each task.
*   **Phase Verification:** Each phase in a track must conclude with a manual verification task.

## 4. Phase Completion Protocol
*   When a phase is finished, the agent must perform a "User Manual Verification" task.
*   Check the system state against the phase goals.
*   Record the results and any deviations.

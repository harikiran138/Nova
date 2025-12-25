# Track Spec: Industrial Safety & UX Hardening

## Overview
This track transforms Nova into an industrial-grade system by implementing explicit health states (SAFE, WARNING, HALT), mandatory dry-run capabilities for destructive actions, and a "Cyberpunk" TUI overhaul that visualizes the agent's reasoning process in real-time.

## Objectives
1.  **System States:** Implement a state machine for `SystemState` (SAFE, WARNING, DEGRADED, HALT) monitored by a `HealthMonitor`.
2.  **Dry-Run Mode:** Update all destructive tools (File, Shell) to support a `--dry-run` flag and log intent without execution.
3.  **TUI Evolution:** Add real-time Plan Tree visualization and an "Explain-Why" panel to the Textual interface.

## Success Criteria
- Agent automatically enters `HALT` state after 3 consecutive tool failures.
- File operations in `dry_run` mode log the path and content but do not touch the disk.
- TUI displays a live tree of the PVEV plan steps.

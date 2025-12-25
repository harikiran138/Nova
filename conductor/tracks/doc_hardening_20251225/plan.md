# Plan: Documentation Refinement & Hardening

Refine project documentation to reflect the industrial-grade Nova Project Overview and archive obsolete materials.

## Phase 0: Pre-Flight Safety Check [checkpoint: 54f8a34]
- [x] Task: Identify Canonical Documents a3ea4d1
- [x] Task: Conductor - User Manual Verification 'Pre-Flight Safety Check' (Protocol in workflow.md) 54f8a34

## Phase 1: Archival and Cleanup
- [ ] Task: Create Archival Infrastructure
    - [ ] Sub-task: Create directory `documentation/archive/`
- [ ] Task: Audit and Move Obsolete Files
    - [ ] Sub-task: Identify files in `documentation/` that are superseded or contradicted by the new overview
    - [ ] Sub-task: Move identified files to `documentation/archive/`
- [ ] Task: Add Archival Headers
    - [ ] Sub-task: Prepend status, reason, and date to each file in `documentation/archive/`
- [ ] Task: Conductor - User Manual Verification 'Archival and Cleanup' (Protocol in workflow.md)

## Phase 2: Core Documentation Updates
- [ ] Task: Update README.md
    - [ ] Sub-task: Integrate the "Improved & Hardened" overview into root `README.md`
- [ ] Task: Update Project Overview
    - [ ] Sub-task: Overwrite `documentation/Project_Overview.md` with the refined content
- [ ] Task: Update Architecture Documentation
    - [ ] Sub-task: Update `documentation/Architecture.md` to align with the core architecture sections (Brain, Body, Memory, Tools)
- [ ] Task: Verify Documentation Consistency
    - [ ] Sub-task: Verify terminology consistency (ReAct, ADK, TUI, Agent Loop) across all canonical docs
- [ ] Task: Conductor - User Manual Verification 'Core Documentation Updates' (Protocol in workflow.md)

## Phase 3: Roadmap and Future Tracks
- [ ] Task: Integrate Roadmap into Documents
    - [ ] Sub-task: Ensure the "Roadmap & Next Steps" section is present in canonical sources
- [ ] Task: Update Project Tracks
    - [ ] Sub-task: Add `trajectory_intelligence` track to `conductor/tracks.md`
    - [ ] Sub-task: Add `adk_tool_expansion` track to `conductor/tracks.md`
    - [ ] Sub-task: Add `reinforcement_learning_loop` track to `conductor/tracks.md`
    - [ ] Sub-task: Ensure new track IDs follow conductor naming conventions
- [ ] Task: Conductor - User Manual Verification 'Roadmap and Future Tracks' (Protocol in workflow.md)
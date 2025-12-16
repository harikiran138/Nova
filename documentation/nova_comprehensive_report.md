# Nova Agent System Report

**Date**: 2025-11-28
**Version**: v1.3
**Status**: Stable / Production-Ready

---

## 1. Executive Summary
**Nova** is a local, privacy-first AI agent designed to act as a pair programmer and autonomous assistant. Unlike cloud-based tools, Nova runs entirely on the user's machine (via Ollama), ensuring zero data leakage and offline capability. It employs a **ReAct (Reason-Act-Observe)** architecture to solve complex tasks by iteratively planning, executing tools, and observing results.

## 2. System Architecture
Nova is built on a modular Python architecture:

*   **Agent Core (`src/agent_core/`)**:
    *   **`AgentLoop`**: The brain. Manages the conversation history, system prompts, and the ReAct loop.
    *   **`Planner`**: Breaks down high-level goals into executable steps.
    *   **`MemoryManager`**: Handles session persistence (save/load/resume).
    *   **`SafetyPolicy`**: Enforces security rules (Read-Only, Sandbox-Only, etc.).
    *   **`Sandbox`**: Provides an isolated environment for risky operations.

*   **Tool Ecosystem (`src/agent_core/tools/`)**:
    *   **Registry**: Central hub for tool registration and dispatch.
    *   **File Tools**: `read`, `write`, `mkdir`, `patch` (surgical edits).
    *   **Git Tools**: `status`, `add`, `commit`, `diff`, `log` (with auto-init).
    *   **Shell Tools**: Controlled command execution with allowlists.
    *   **Web/API Tools**: Search, weather, etc. (extensible).

*   **Interfaces**:
    *   **CLI (`nova`)**: Rich terminal interface with spinners, panels, and interactive chat.
    *   **TUI (`nova ui`)**: Full-screen Textual app with command palette (v1.1).

## 3. Current Capabilities (v1.3)
*   **Persistence**: Sessions are saved automatically. Resume work anytime with `nova run --resume`.
*   **Smart Git**: Automatically initializes repositories and manages version control.
*   **Robustness**: Self-correcting tool calls (fixes JSON errors automatically).
*   **UX**: Polished visual feedback, typing effects, and helpful tips.
*   **Safety**: Strict sandbox mode prevents accidental system damage.

---

## 4. Improvement Roadmap (The Future of Nova)

To elevate Nova from a "Tool" to a "Platform", we propose the following upgrades:

### Phase 1: Intelligence & Context (v1.4)
*   **RAG (Retrieval-Augmented Generation)**:
    *   *Goal*: Allow Nova to "read" the entire codebase, not just open files.
    *   *Impl*: Use `chromadb` or `faiss` to index the workspace.
*   **Multi-Agent Orchestration**:
    *   *Goal*: Specialized agents working together.
    *   *Impl*: A "Supervisor" agent that delegates to "Coder", "Researcher", and "Reviewer" agents.
*   **Voice Interface**:
    *   *Goal*: Talk to Nova.
    *   *Impl*: Integrate Whisper (STT) and a local TTS engine.

### Phase 2: Connectivity & Expansion (v1.5)
*   **Plugin System**:
    *   *Goal*: Allow users to add custom tools without modifying core code.
    *   *Impl*: Load python scripts from `~/.nova/plugins/`.
*   **IDE Integration**:
    *   *Goal*: Nova inside VS Code.
    *   *Impl*: A VS Code extension that communicates with the Nova CLI/API.
*   **Docker Integration**:
    *   *Goal*: True sandboxing.
    *   *Impl*: Run the `Sandbox` environment inside a Docker container for 100% isolation.

### Phase 3: The "Nova Platform" (v2.0)
*   **Web Interface**:
    *   *Goal*: A beautiful dashboard for managing tasks, viewing history, and visualizing agent thought processes.
    *   *Impl*: Next.js + FastAPI backend.
*   **Fine-Tuned Models**:
    *   *Goal*: A model specifically trained on Nova's tool definitions.
    *   *Impl*: Fine-tune Llama-3 on a dataset of Nova tool calls for higher accuracy.
*   **Cloud Sync (Optional)**:
    *   *Goal*: Sync sessions between work and home machines.
    *   *Impl*: Encrypted sync to a user-provided S3 bucket or Git repo.

## 5. Conclusion
Nova v1.3 is a robust foundation. By focusing on **Context (RAG)** and **Orchestration (Multi-Agent)** next, we can exponentially increase its problem-solving capability.

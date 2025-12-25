# Nova Project Overview

## 1. Executive Summary
**Nova** is an industrial-grade, local-first autonomous AI agent designed for power users. It prioritizes privacy, uncensored operation, and "clean and work it perfect" reliability. Nova interacts with the user through a highly aesthetic, Cyberpunk-themed Terminal User Interface (TUI) and uses a sophisticated ReAct (Reason-Act-Observe) loop to execute complex tasks autonomously.

## 2. Core Architecture

### **Brain: The Agent Loop**
*   **Location**: `src/agent_core/agent_loop.py`
*   **Model**: ReAct (Reason-Act-Observe) pattern.
*   **Engine**: Drives the agent's decision-making process, integrating tool usage, memory, and safety checks.
*   **Recent Fixes**: Resolved `NameError` in prompt handling and fixed `temperature` configuration.

### **Body: The "Cyberpunk" TUI**
*   **Location**: `src/ui/nova_tui.py`
*   **Framework**: Built with `Textual` and `Rich`.
*   **Theme**: `Cyberpunk Neon` (Green/Magenta/Cyan palette on dark background).
*   **Layout**: Three-pane design:
    1.  **Chat Window**: Main interaction area.
    2.  **Mission Plan**: Visualization of the agent's decision tree (`PlanTree`).
    3.  **Active Tools**: Status of available capabilities.

### **Memory & Knowledge**
*   **Short-term**: In-memory conversation history with smart pruning.
*   **Long-term**: ChromaDB vector store (`src/agent_core/learning/memory.py`).
*   **Learning**: Trajectory logging (`src/agent_core/learning/trajectory.py`) captures interaction steps for future reinforcement learning.

### **Tools (ADK)**
*   **Registry**: `src/agent_core/adk/registry.py` discovers and manages tools.
*   **Capabilities**:
    *   **File System**: Safe file operations.
    *   **Web**: Search and Extract mechanisms.
    *   **Vision**: Google AI Edge (MediaPipe) integration for local image analysis.

## 3. Technology Stack

*   **Language**: Python 3.8+
*   **Inference**: Ollama (Local LLM serving).
*   **UI**: Textual, Rich.
*   **Data**: ChromaDB (Vector Store), JSON (Configuration & Logs).
*   **Infrastructure**: Docker (Sandboxing), Git (Version Control).

## 4. Current Status (As of Latest Session)

### **✅ Operational**
*   **CLI & TUI**: Fully functional. TUI launches with correct theming and layout.
*   **Agent Logic**: Debugged and verified.
    *   Successfully responds to prompts (e.g., "tell me a joke").
    *   Logs interaction trajectories to `.nova/trajectories/`.
*   **Git Sync**:
    *   All local changes (including critical fixes) pushed to `origin main`.
    *   Rebase conflicts in `agent_loop.py`, `nova_tui.py`, and `tracks.md` resolved.

### **🛠 Key Files**
*   `src/nova_cli.py`: Entry point for the application.
*   `src/agent_core/config.py`: Configuration management (Env vars, Defaults).
*   `src/agent_core/model_client.py`: Interface to Ollama API.

## 5. Next Steps (Recommended)
*   **Trajectory Analysis**: Build a viewer or analyzer for the JSON logs to improve agent performance.
*   **Tool Expansion**: Add more complex tools via the ADK (e.g., advanced coding tools, system automation).
*   **Reinforcement Learning**: Implement the feedback loop using the captured trajectories.

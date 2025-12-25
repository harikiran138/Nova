# Tech Stack - Nova

## Backend & Core
- **Language**: Python (>=3.8) - Chosen for its extensive AI/ML ecosystem and ease of tool integration.
- **Inference Engine**: Ollama - Provides high-performance, local LLM serving without external dependencies.
- **Agent Architecture**: ReAct (Reason-Act-Observe) Loop - Enables autonomous planning and tool execution.

## Interface
- **TUI Framework**: `rich` - Used to build the highly aesthetic, interactive "Cyberpunk" terminal interface.

## Infrastructure & Security
- **Sandboxing**: Docker - Ensures safe execution of agent actions in isolated environments.
- **Communication**: `requests` - Standard library for interacting with local and remote APIs (like Ollama).
# System Architecture

## High-Level Design
Nova Agent CLI follows a modular design with a clear separation between the CLI interface, the agent logic, and the tool implementations.

### Components

1.  **CLI Entry Point (`src/nova_cli.py`)**
    - Handles command-line argument parsing.
    - Manages the interactive REPL loop.
    - Initializes the agent and configuration.

2.  **Agent Core (`src/agent_core/`)**
    - **`config.py`**: Manages configuration loading from environment variables and validation.
    - **`tools.py`**: Implements the `ToolRegistry` and individual tools (`file.*`, `shell.*`, `web.*`). Handles safety checks and sandboxing.
    - **`model_client.py`**: Client for communicating with the Ollama API.
    - **`agent_loop.py`**: Implements the ReAct (Reasoning + Acting) loop, coordinating between the model and tools.

3.  **Workspace (`workspace/`)**
    - A sandboxed directory where all file operations are restricted to.

### Detailed Subsystems

#### **Brain: The Agent Loop**
- **Location**: `src/agent_core/agent_loop.py`
- **Model**: ReAct (Reason-Act-Observe) pattern.
- **Function**: It drives the agent's decision-making process, integrating tool usage, memory, and safety checks. It now supports `temperature` configuration for more creative or deterministic outputs.

#### **Body: The User Interface**
- **Framework**: Built with `Textual` and `Rich`.
- **Theme**: `Cyberpunk Neon` (Green/Magenta/Cyan palette on dark background).
- **Layout**:
    1.  **Chat Window**: Main interaction area.
    2.  **Mission Plan**: Visualization of the agent's decision tree (`PlanTree`).
    3.  **Active Tools**: Status of available capabilities.

#### **Memory & Knowledge**
- **Short-term**: In-memory conversation history with smart pruning.
- **Long-term**: ChromaDB vector store (`src/agent_core/learning/memory.py`).
- **Learning**: Trajectory logging (`src/agent_core/learning/trajectory.py`) captures interaction steps (input, thought, tool call, response) to `.nova/trajectories/` for future reinforcement learning.

## Data Flow
1.  **User Input**: User types a command in the CLI.
2.  **Agent Processing**: The `agent_loop` sends the input to the Ollama model.
3.  **Tool Selection**: The model decides if a tool is needed and generates a tool call (JSON).
4.  **Tool Execution**: `ToolRegistry` (ADK) parses the call, validates safety, and executes the tool.
5.  **Observation**: The tool output is fed back to the model.
6.  **Response**: The model generates a final response to the user.

## Security Model
- **Sandboxing**: File operations are strictly limited to the `workspace` directory.
- **Allowlisting**: Shell commands are restricted to a configurable allowlist.
- **Pattern Matching**: Destructive shell commands (e.g., `rm -rf`) are blocked by regex patterns.

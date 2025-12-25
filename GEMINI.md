# Nova Agent CLI

## Project Overview

**Nova** is an industrial-grade, local-first autonomous AI agent designed for power users, software engineers, and DevOps professionals. It operates entirely locally using **Ollama**, ensuring zero latency, zero API costs, and 100% privacy.

Nova features a sophisticated **ReAct (Reason-Act-Observe) loop** that allows it to execute complex tasks, debug code, and manage infrastructure autonomously. It provides two main interfaces:
1.  A **Cyberpunk-themed Terminal User Interface (TUI)** built with Python (`rich`, `textual`).
2.  A **Modern Web UI** built with React and Vite.

### Key Features
*   **Local Inference:** Powered by Ollama (7B–70B+ models).
*   **Autonomous Agent:** ReAct loop for multi-step problem solving.
*   **Dual Interfaces:** CLI/TUI for terminal lovers, Web UI for visual interaction.
*   **Extensible:** Agent Developer Kit (ADK) for adding custom tools.
*   **Safe:** Sandboxed execution with configurable security levels.

## Architecture & Tech Stack

The project is structured into several components:

*   **Core Logic (`src/`, `nova-core/`):** Python 3.8+. Implements the agent loop, memory (ChromaDB), and tool orchestration.
*   **CLI/TUI:** Entry point via `src.nova_cli:main`.
*   **API (`nova-api/`):** Backend service to expose agent capabilities (likely FastAPI).
*   **Web UI (`nova-ui/`):** React 19 + TypeScript + Vite frontend.
*   **Infrastructure:** Docker Compose for orchestrating the API, UI, and Ollama integration.

## Building and Running

### Prerequisites
*   **Python 3.8+**
*   **Node.js & npm** (for Web UI)
*   **Docker & Docker Compose** (recommended)
*   **Ollama** (running locally with a model pulled, e.g., `ollama pull mannix/llama3.1-8b-abliterated`)

### Option 1: Docker (Recommended)
This brings up the full stack (API + UI).

```bash
# Start all services
docker compose up -d

# Access the Web UI at http://localhost:5173
# Access the API at http://localhost:8000
```

To run the CLI inside the container:
```bash
docker exec -it nova_agent nova ui
```

### Option 2: Local Development

#### 1. CLI / Core
```bash
# Install dependencies and the package in editable mode
pip install -e .

# Run the CLI
nova
# OR specific commands
nova task run "Analyze this repo"
```

#### 2. Web UI (`nova-ui/`)
```bash
cd nova-ui
npm install
npm run dev
```

## Development Conventions

*   **Code Style:** Follows standard Python (PEP 8) and TypeScript conventions.
*   **Project Structure:**
    *   `src/`: Main Python source for the CLI/Agent.
    *   `nova-api/`: Backend API service.
    *   `nova-ui/`: Frontend application.
    *   `documentation/`: Comprehensive guides on architecture, testing, and usage.
*   **Testing:** Tests are located in the `tests/` directory. Run them using `pytest`.
*   **Configuration:** Managed via `.env` file (see `.env.example`). Key variables include `MODEL_PROVIDER`, `OLLAMA_MODEL`, and `TURBO_MODE`.

## Key Documentation Files
*   `README.md`: Main entry point and feature summary.
*   `documentation/Project_Overview.md`: Detailed architectural overview.
*   `documentation/nova_v2_architecture.md`: Specifics on V2 architecture.
*   `documentation/nova_tools_reference.md`: Guide to available agent tools.

# Nova v2 Architecture Proposal

## 1. High-Level Overview

Nova v2 transitions from a simple CLI script to a modular, service-oriented platform. The core logic is decoupled from the interface, allowing multiple clients (CLI, Web UI, Desktop) to interact with the same intelligent agent engine.

### System Components

```mermaid
graph TD
    subgraph Clients
        CLI[Nova CLI]
        Web[Nova Web UI]
        Desktop[Nova Desktop (Tauri)]
    end

    subgraph "Nova Platform (Docker/Local)"
        API[FastAPI Gateway]
        
        subgraph "Nova Core"
            Engine[Agent Engine]
            Router[Model Router]
            Memory[Memory Store (SQLite/Vector)]
        end
        
        subgraph "Tool Ecosystem"
            Tools[Tool Registry]
            FS[File System]
            Shell[Shell Executor]
            Browser[Web Browser]
            Git[Git Assistant]
            More[...]
        end
        
        Ollama[Ollama Service]
    end

    CLI --> API
    Web --> API
    Desktop --> API
    
    API --> Engine
    Engine --> Router
    Engine --> Memory
    Engine --> Tools
    
    Router --> Ollama
    Tools --> FS
    Tools --> Shell
    Tools --> Browser
```

## 2. Component Details

### 2.1 Nova Core (`nova-core`)
The brain of the operation.
*   **Agent Engine**: Implements the reasoning loop (ReAct, Plan-and-Solve). Handles context management and prompt construction.
*   **Model Router**: Dynamically selects the best model for the task (e.g., `llama3` for reasoning, `gemma` for quick summaries).
*   **Memory System**:
    *   **Short-term**: Conversation history (in-memory/Redis).
    *   **Long-term**: SQLite database for structured data (user profiles, preferences) and vector store for semantic search.

### 2.2 Tool Ecosystem (`nova-tools`)
A plugin-based system where tools are defined with JSON schemas.
*   **Standard Library**: File I/O, Shell, System Info.
*   **Extended Library**: Web Scraper, PDF Reader, Git, Database, etc.
*   **Safety Layer**: All tool executions pass through a permission/confirmation layer.

### 2.3 Interfaces
*   **API Gateway**: A FastAPI server exposing REST endpoints and WebSockets for streaming responses.
*   **Nova CLI**: A lightweight Python client that connects to the API (or imports Core directly for standalone mode).
*   **Nova UI**: A React + Vite Single Page Application (SPA) for a rich chat experience, memory visualization, and settings.

## 3. Data Flow

### Chat Interaction Flow
1.  **User Input**: User sends a message via CLI or Web UI.
2.  **API Handling**: Request hits FastAPI, upgrades to WebSocket.
3.  **Context Retrieval**: Agent fetches relevant memory and conversation history.
4.  **Planning**: Agent generates a thought/plan using the Main Model.
5.  **Tool Selection**: Agent decides to call a tool (e.g., `web.search`).
6.  **Execution**: Tool executes (sandbox check applied). Output returned to Agent.
7.  **Observation**: Agent analyzes tool output.
8.  **Response**: Agent streams final answer to User via WebSocket.
9.  **Archival**: Interaction saved to Long-term Memory.

## 4. Directory Structure

```
nova-v2/
├── nova-core/              # Core logic package
│   ├── engine/             # Agent loops
│   ├── memory/             # SQLite/Vector logic
│   ├── models/             # Ollama client & router
│   └── utils/
├── nova-tools/             # Tool definitions
│   ├── standard/           # Built-in tools
│   └── extended/           # Extra capabilities
├── nova-api/               # FastAPI backend
│   ├── routers/
│   └── main.py
├── nova-cli/               # Command line interface
├── nova-ui/                # React Web App
│   ├── src/
│   └── public/
├── docker-compose.yml
└── README.md
```

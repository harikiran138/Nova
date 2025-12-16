# Nova Privacy Model

**Version**: 2.2 (Private Autonomous Edition)

## Core Principles

Nova is designed with a "Local-First, Privacy-First" architecture. Unlike cloud-based assistants that stream your data to external servers by default, Nova operates as a self-contained entity on your machine.

### 1. Identity Protection
*   **Self-Sovereign**: Nova identifies simply as "Nova". It does not expose the underlying model provider (e.g., Google, OpenAI, Ollama) in its persona.
*   **No Leakage**: Internal system prompts, chain-of-thought reasoning, and model parameters are hidden from the user interface to maintain a clean, professional interaction.

### 2. Offline by Default
*   **Default State**: Nova starts in `Offline Mode`.
*   **Network Access**: Any attempt to access the internet (via `NetTool`) is blocked by default.
*   **Consent**: You must explicitly grant permission for network operations, or disable offline mode globally.

### 3. Data Containment
*   **Local Storage**: All conversation history, memory, and artifacts are stored locally in your workspace (`.nova/` directory).
*   **No Telemetry**: Nova does not send usage data, crash reports, or analytics to any third party.
*   **Audit Log**: A local audit log records all actions for your review, but this log never leaves your machine.

## Configuration

### Enabling Network Access
To allow Nova to access the internet, you can:
1.  **Per-Session**: Respond "yes" when prompted during a task.
2.  **Global**: Set `NOVA_OFFLINE_MODE=false` in your environment or `.env` file.

### Sandbox
Nova runs file operations within a strict sandbox directory (`WORKSPACE_DIR`). It cannot access files outside this directory unless explicitly configured.

> **ARCHIVED**: Superseded by [Project_Overview.md](../Project_Overview.md) on 2025-12-25.

# ARCHIVED
**Status:** Archived
**Reason:** Superseded by the Refined, Industrial-Grade Nova Project Overview (Dec 2025)
**Date:** 2025-12-25

---

# Nova Agent CLI - Improvement Plan

## 🔧 Immediate Actions (Fixes)

1.  **Create `.env.example`**
    - **Priority**: High
    - **Reason**: Referenced in README but missing from files.
    - **Action**: Create the file with default values.
    ```bash
    OLLAMA_BASE_URL=http://127.0.0.1:11434
    OLLAMA_MODEL=llama3
    WORKSPACE_DIR=./workspace
    ALLOW_SHELL_COMMANDS=true
    SHELL_COMMAND_ALLOWLIST=ls,cat,echo,pwd,python,python3,node,npm,git,curl,wget,head,tail,grep,find
    ```

## 🚀 Future Improvements

1.  **Enhanced Tooling**
    - Add a `search.code` tool (using `grep` or `ripgrep`) for better codebase exploration.
    - Add a `git.commit` tool to allow the agent to save its work.

2.  **Conversation Memory**
    - Currently, memory is in-memory only. Implement persistence (e.g., `history.json` or SQLite) to save conversations across sessions.

3.  **Model Flexibility**
    - Add support for other backends (e.g., OpenAI compatible APIs) in `model_client.py` to allow using cloud models if desired.

4.  **Interactive TUI**
    - Upgrade from a simple REPL to a full TUI (Text User Interface) using `Textual` (built on `rich`) for a more IDE-like experience in the terminal.
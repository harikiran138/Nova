> **ARCHIVED**: Superseded by [Project_Overview.md](../Project_Overview.md) on 2025-12-25.

# ARCHIVED
**Status:** Archived
**Reason:** Superseded by the Refined, Industrial-Grade Nova Project Overview (Dec 2025)
**Date:** 2025-12-25

---

# Nova v2 Feature Plan

## 1. Multi-Interface Experience
*   **Web UI (React + Vite)**:
    *   Modern Chat Interface (ChatGPT-style).
    *   Markdown rendering with syntax highlighting.
    *   Collapsible "Thought Process" logs to see agent reasoning.
    *   Sidebar for Chat History and Memory Management.
    *   Settings panel for Model selection and Tool configuration.
    *   Dark/Light mode support.
*   **CLI (Rich)**:
    *   Streaming text output.
    *   Interactive spinner for tool execution.
    *   Command history and auto-completion.

## 2. Advanced Agent Intelligence
*   **Structured Reasoning**: Move beyond simple prompt loops to structured ReAct (Reasoning + Acting) patterns.
*   **Memory Persistence**:
    *   **SQLite**: Store conversations, user preferences, and structured tool data.
    *   **Vector Search** (Optional): Semantic retrieval of past knowledge.
*   **Role Profiles**: Ability to switch personas (e.g., "Senior Dev", "Technical Writer") which adjust system prompts and tool access.

## 3. Expanded Tool Ecosystem (10+ Tools)
1.  **File System**: Read, Write, List, Search (with safety sandbox).
2.  **Shell Executor**: Run commands with allowlist/confirmation.
3.  **Web Browser**: `playwright` or `requests` based fetcher with text extraction.
4.  **PDF Reader**: Extract text and tables from PDFs.
5.  **System Monitor**: Real-time CPU, RAM, Disk usage.
6.  **Git Assistant**: Status, Diff, Commit, Log.
7.  **Database Tool**: Execute SQL queries on local SQLite DBs.
8.  **API Caller**: Generic HTTP client for external APIs.
9.  **Image Generation**: Integration with Ollama multi-modal or external APIs.
10. **Calendar/Reminders**: Local JSON-based task/reminder store.

## 4. Model Enhancement
*   **Multi-Model Support**: Configurable list of available models.
*   **Smart Routing**:
    *   Use `llama3` (or larger) for complex planning.
    *   Use `gemma` (or smaller) for simple tool output formatting.
*   **Context Window Management**: Sliding window or summarization for long conversations.

## 5. Automated Quality System
*   **Self-Correction**: Agent checks its own output format before sending.
*   **Feedback Loop**: User thumbs up/down in UI feeds back into prompt tuning (local log).
*   **Benchmarking**: Script to run standard queries and measure success rate and latency.
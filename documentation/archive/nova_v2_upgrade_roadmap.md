> **ARCHIVED**: Superseded by [Project_Overview.md](../Project_Overview.md) on 2025-12-25.

# ARCHIVED
**Status:** Archived
**Reason:** Superseded by the Refined, Industrial-Grade Nova Project Overview (Dec 2025)
**Date:** 2025-12-25

---

# Nova v2 Upgrade Roadmap

| Phase | Milestone | Description | Est. Time |
| :--- | :--- | :--- | :--- |
| **1** | **Architecture & Core** | Refactor into `nova-core`, implement ReAct engine, SQLite memory. | Day 1 |
| **2** | **Tool Expansion** | Implement the 10+ requested tools in `nova-tools`. | Day 1-2 |
| **3** | **API & Backend** | Build FastAPI server with WebSocket support. | Day 2 |
| **4** | **Web UI** | Develop React+Vite frontend. | Day 2-3 |
| **5** | **Integration** | Connect UI to API, update Docker Compose. | Day 3 |
| **6** | **Testing & Polish** | End-to-end tests, benchmarks, documentation. | Day 3 |

## Detailed Steps

### Phase 1: Core Engine
1.  Create `nova-core` python package.
2.  Migrate `OllamaClient` and `AgentLoop` logic.
3.  Enhance `AgentLoop` to support structured ReAct.
4.  Add `MemoryManager` with SQLite backend.

### Phase 2: Tools
1.  Create `nova-tools` package.
2.  Port existing tools (File, Shell, Web).
3.  Implement new tools (Git, PDF, System, etc.).
4.  Add `ToolRegistry` with auto-discovery.

### Phase 3: API
1.  Create `nova-api` package.
2.  Setup FastAPI app.
3.  Create `/chat` WebSocket endpoint.
4.  Create `/tools` and `/models` REST endpoints.

### Phase 4: UI
1.  Initialize Vite project `nova-ui`.
2.  Setup Tailwind CSS and Shadcn/UI (or similar).
3.  Build Chat Component, Sidebar, and Settings.
4.  Implement WebSocket client.

### Phase 5: Infrastructure
1.  Update `docker-compose.yml` to include `nova-api` and `nova-ui` (nginx/node).
2.  Ensure network connectivity between containers.

### Phase 6: Verification
1.  Write `tests/` suite.
2.  Run `pytest`.
3.  Manual verification of UI flows.
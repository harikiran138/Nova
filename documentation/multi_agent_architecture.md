# Multi-Agent Architecture

## Overview
Nova v2.0 introduces a multi-agent system where specialized agents collaborate to solve complex tasks.

## Agents
### 1. Supervisor (Orchestrator)
- **Role**: Breaks down user goals and delegates to specialized agents.
- **Tools**: `delegate`, `plan`.

### 2. Coder (Specialist)
- **Role**: Writes, debugs, and refactors code.
- **Tools**: `file.*`, `git.*`, `code.*`.
- **Profile**: High temperature for creativity, strict syntax rules.

### 3. Researcher (Specialist)
- **Role**: Gathers information from the web or documentation.
- **Tools**: `search.web`, `rag.search`.

## Workflow
1. **User** inputs a goal: "Build a React app."
2. **Supervisor** analyzes request and creates a plan.
3. **Supervisor** delegates "Scaffold project" to **Coder**.
4. **Coder** executes tools and reports back.
5. **Supervisor** delegates "Find best practices" to **Researcher**.
6. **Supervisor** synthesizes results and reports to User.

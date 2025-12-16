# Nova v2 Test Strategy

## 1. Testing Levels

### 1.1 Unit Tests (`nova-core`, `nova-tools`)
*   **Goal**: Verify individual components work in isolation.
*   **Tools**: `pytest`, `unittest.mock`.
*   **Coverage**:
    *   Tool input validation.
    *   Memory storage/retrieval.
    *   Prompt construction.
    *   Router logic.

### 1.2 Integration Tests (`nova-api`)
*   **Goal**: Verify API endpoints and WebSocket communication.
*   **Tools**: `pytest-asyncio`, `httpx`.
*   **Coverage**:
    *   REST endpoint responses.
    *   WebSocket connection and message streaming.
    *   Database persistence.

### 1.3 End-to-End (E2E) Tests
*   **Goal**: Verify the full system from User Input to Agent Response.
*   **Tools**: Custom Python scripts, potentially `Playwright` for UI.
*   **Coverage**:
    *   Full conversation flows.
    *   Complex tool usage (e.g., "Read file -> Summarize -> Write file").
    *   Docker container interaction.

## 2. Automated Test Suite Plan

We will create a `tests/` directory with the following structure:

```
tests/
├── unit/
│   ├── test_core_engine.py
│   ├── test_memory.py
│   └── test_tools/
├── integration/
│   └── test_api.py
└── e2e/
    └── test_scenarios.py
```

## 3. Performance Benchmarking

*   **Latency**: Measure time to first token (TTFT) and total response time.
*   **Success Rate**: Run a set of 50 standard prompts (e.g., "What is 2+2?", "Summarize this file") and verify correct tool usage.

## 4. Quality Report
A script will generate `documentation/nova_v2_quality_report.md` containing:
*   Test pass/fail counts.
*   Benchmark results.
*   Identified bottlenecks.

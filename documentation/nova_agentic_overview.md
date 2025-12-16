# Nova Agentic System Overview

Nova has been upgraded to a true agentic system, capable of understanding high-level goals, planning steps, and executing them using a modular toolset.

## Core Components

### 1. Planner
The **Planner** (`src/agent_core/planner.py`) is responsible for breaking down a user's high-level goal into a structured list of steps. It uses the LLM to analyze the goal and available tools, producing a JSON-based plan.

### 2. Task
A **Task** (`src/agent_core/tasks.py`) represents a unit of work. It contains:
- **Goal**: The user's original request.
- **Steps**: A sequence of sub-tasks to achieve the goal.
- **Status**: Current state (pending, in_progress, completed, failed).
- **History**: A log of all tool executions and model responses.

### 3. Modular Tools
Tools are now organized in `src/agent_core/tools/`. Each tool is a self-contained class inheriting from `BaseTool`.
- **File Tools**: Read, write, list files.
- **Shell Tools**: Execute safe shell commands.
- **Web Tools**: Fetch content from URLs.

### 4. Agent Loop
The **Agent Loop** (`src/agent_core/agent_loop.py`) orchestrates execution.
- **`run_task(task)`**: Iterates through the planned steps.
- **Dynamic Execution**: If a step has a pre-defined tool, it executes it. If not, it asks the agent to decide the best action.

## How It Works

1.  **User Request**: `nova task run "Create a Flask app"`
2.  **Planning**: The Planner asks the model to generate a plan.
    - *Step 1: Create app.py*
    - *Step 2: Create requirements.txt*
3.  **Execution**: The Agent Loop executes each step.
    - *Step 1*: Calls `file.write("app.py", ...)`
    - *Step 2*: Calls `file.write("requirements.txt", ...)`
4.  **Completion**: The task is marked as completed.

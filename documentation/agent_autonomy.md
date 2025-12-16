# Agent Autonomy & Multi-Agent Brain

**Version**: 2.2

## Architecture

Nova employs a multi-agent architecture to handle complex tasks. Instead of a single loop, tasks are decomposed and assigned to specialized "personas".

### The Supervisor
The **Supervisor** is the high-level planner. It:
1.  Analyzes the user's goal.
2.  Breaks it down into sequential steps.
3.  Assigns a **Role** to each step.

### Roles
*   **General**: Standard task execution.
*   **Researcher**: Specialized in gathering information (Web Search, API calls).
*   **Coder**: Specialized in writing and debugging code.
*   **Reviewer**: specialized in validating output and checking for errors.

## Execution Flow
1.  **Plan**: The Supervisor generates a JSON plan with roles.
2.  **Delegate**: The Agent Loop iterates through the steps.
3.  **Execute**: The step is executed using the tools appropriate for the role.
4.  **Observe**: The result is captured.
5.  **Refine**: If a step fails, the agent attempts to self-correct or replan.

## Self-Correction
Nova includes an auto-retry mechanism. If a tool call fails (e.g., syntax error, network timeout), Nova analyzes the error message and attempts a corrected call without user intervention, up to a limit.

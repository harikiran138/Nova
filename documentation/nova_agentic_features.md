# Nova Agentic Features

Nova v2 introduces a powerful "Reason-and-Act" (ReAct) agent architecture, making it capable of complex reasoning and autonomous tool usage.

## ReAct Architecture
Nova's agent loop now follows a strict cognitive cycle:
1.  **Reason**: Analyze the situation and plan the next step.
2.  **Act**: Select and execute the appropriate tool.
3.  **Observe**: Analyze the tool's output.
4.  **Respond**: Communicate with the user or continue to the next step.

## Task System
Nova can handle multi-step tasks with state tracking.

### CLI Commands
- `nova task plan "Goal"`: Generate a step-by-step plan without executing.
- `nova task run "Goal"`: Generate a plan and execute it autonomously.

## Safety & Sandbox
Nova includes a robust safety system:
- **Sandbox Mode**: Restricts file and shell operations to `~/.nova/sandbox`.
- **Safety Levels**:
    - `READ_ONLY`: No modifications allowed.
    - `SANDBOX_ONLY`: Modifications only in sandbox (Default for Coder).
    - `UNRESTRICTED`: Full system access (Use with caution).

## Profiles
- **General**: Balanced helper.
- **Coder**: Specialized in software engineering, defaults to Sandbox mode, has access to Git and Patch tools.
- **Researcher**: Focused on information gathering, has access to Web and Search tools.

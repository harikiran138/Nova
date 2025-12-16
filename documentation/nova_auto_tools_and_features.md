# Auto-Tools & Features

Nova v2 introduces intelligent automatic tool selection and feature toggling based on your goal and the active agent profile.

## How it Works
Instead of overwhelming the model with every possible tool, Nova filters the available tools to match the current context. This improves accuracy and reduces hallucinations.

### Tool Selection Logic
1.  **Agent Profile**: Each agent profile (e.g., `coder`, `researcher`) defines a list of `allowed_tools` patterns (e.g., `file.*`, `web.get`).
2.  **Goal Analysis**: (Future) Nova will analyze your goal to further refine the toolset.
3.  **Active Tools**: Only the selected tools are presented to the model in the system prompt.

## Sandbox Integration
Nova is now "Sandbox Aware".
- **Sandbox Mode**: When active, the agent is explicitly told it is in a sandbox environment.
- **Default Behavior**: The `coder` profile enables Sandbox Mode by default.
- **Safety**: In Sandbox Mode, file operations are restricted to the sandbox directory (`~/.nova/sandbox`).

## CLI Usage
You can override these behaviors using CLI flags:

```bash
# Force sandbox mode
nova run --sandbox "Build a dangerous script"

# Select a specific agent
nova run --agent researcher "Find information about X"

# Check status
nova --agent coder --sandbox status
```

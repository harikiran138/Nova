# Autonomy & Safety (Nova v2.1)

Nova v2.1 operates with a high degree of autonomy while enforcing strict safety protocols.

## The Autonomous Loop

1.  **Plan**: Analyze user request and break it down into steps.
2.  **Act**: Select the appropriate tool.
3.  **Validate**: Check safety permissions.
4.  **Execute**: Run the tool.
5.  **Reflect**:
    *   **Success**: Proceed to next step.
    *   **Failure**: Analyze error, adjust plan, and retry.

## Safety Guardian

The `SafetyPolicy` enforces rules based on the active mode:

| Mode | File Writes | Shell Execution | Dangerous Commands |
|---|---|---|---|
| `READ_ONLY` | ❌ | ❌ | ❌ |
| `SANDBOX_ONLY` | ✅ (Sandbox) | ✅ (Sandbox) | ❌ (Blocked) |
| `RESTRICTED` | ✅ | ✅ | ⚠️ **Confirm** |
| `UNRESTRICTED` | ✅ | ✅ | ✅ |

### Dangerous Commands
Commands like `rm`, `kill`, `chmod`, `wget`, `curl` (in shell) trigger a **Confirmation Prompt**:

> ❗ SAFETY WARNING: Tool 'shell.run' is potentially dangerous.
> Args: {'command': 'rm -rf /tmp/data'}
> Do you want to proceed? [y/n]

### Audit Log
All actions are logged to `~/.nova/audit.log` with:
*   Timestamp
*   Action/Tool
*   Arguments
*   Allowed/Denied Status
*   Reason

## Error Recovery
If a tool fails (e.g., "Command not found"), Nova enters a **Reflection Phase**:
1.  Reads the error message.
2.  Checks available tools.
3.  Attempts an alternative (e.g., `apt install` if missing, or use a different tool).

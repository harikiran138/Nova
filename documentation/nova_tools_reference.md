# Nova Tools Reference

This document lists the tools available to the Nova agent.

## File Tools
Tools for managing files within the workspace.

### `file.read`
Reads the content of a file.
- **Args**: `path` (string) - Path to the file (relative to workspace).
- **Example**: `{"tool": "file.read", "args": {"path": "README.md"}}`

### `file.write`
Writes content to a file. Creates parent directories if needed.
- **Args**:
    - `path` (string) - Path to the file.
    - `content` (string) - Content to write.
- **Example**: `{"tool": "file.write", "args": {"path": "notes.txt", "content": "Hello"}}`

### `file.list`
Lists files and directories in a given path.
- **Args**: `path` (string, optional) - Directory to list (default: ".").
- **Example**: `{"tool": "file.list", "args": {"path": "src"}}`

## Shell Tools
Tools for executing system commands.

### `shell.run`
Executes a shell command. Restricted to an allowlist and safe patterns.
- **Args**: `command` (string) - Command to execute.
- **Allowed Commands**: `ls`, `cat`, `grep`, `find`, `pwd`, `echo`, `python3`, `pip`, `git`, `mkdir`, `cp`, `mv`, `rm` (safe usage only).
- **Safety**: Blocks `rm -rf`, `mkfs`, and other destructive patterns. Allows `> /dev/null`.
- **Example**: `{"tool": "shell.run", "args": {"command": "ls -la"}}`

## Web Tools
Tools for interacting with the internet.

### `web.get`
Fetches the text content of a URL.
- **Args**: `url` (string) - URL to fetch (must be http/https).
- **Example**: `{"tool": "web.get", "args": {"url": "https://example.com"}}`

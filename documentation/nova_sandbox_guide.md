# Nova Sandbox Guide

The Nova Sandbox is a safe, isolated environment for letting the agent build projects, write code, and execute tasks without risking your main filesystem.

## What is the Sandbox?
By default, the sandbox is located at `~/.nova/sandbox`. When you run a sandbox command, Nova treats this directory as its workspace. It cannot read or write files outside of this directory.

## Commands

### `nova sandbox init`
Initializes the sandbox directory if it doesn't exist.
```bash
nova sandbox init
```

### `nova sandbox info`
Shows the location, file count, and size of the sandbox.
```bash
nova sandbox info
```

### `nova sandbox clean`
**WARNING**: Safely wipes the entire sandbox directory. Use this to start fresh.
```bash
nova sandbox clean
```

### `nova sandbox build "GOAL"`
The most powerful command. It plans and executes a task *inside* the sandbox.
```bash
nova sandbox build "Create a Flask app with a hello world route"
```

## Example Workflow

1.  **Start fresh**:
    ```bash
    nova sandbox clean
    ```

2.  **Build a tool**:
    ```bash
    nova sandbox build "Create a python script that calculates fibonacci numbers"
    ```

3.  **Verify**:
    ```bash
    ls ~/.nova/sandbox
    python3 ~/.nova/sandbox/fib.py
    ```

## Safety Guarantees
- **Path Restriction**: File tools (`file.read`, `file.write`) verify that paths are within the sandbox.
- **Shell Restriction**: Shell commands are executed with the sandbox as the working directory.
- **Destructive Commands**: `rm -rf` and similar commands are blocked by the shell tool's safety filter.

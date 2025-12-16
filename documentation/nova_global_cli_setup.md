# Global CLI Setup Guide

This guide explains how to install Nova globally so you can run the `nova` command from any directory.

## Prerequisites
- Python 3.8 or higher
- Ollama installed and running

## Installation

1.  **Navigate to the project root**:
    ```bash
    cd /path/to/nova-agent-cli
    ```

2.  **Install with pip**:
    ```bash
    pip install .
    ```
    
    *For development (changes reflected immediately):*
    ```bash
    pip install -e .
    ```

3.  **Verify Installation**:
    Open a new terminal window and run:
    ```bash
    nova --help
    ```

## Usage
Once installed, `nova` works like any other system command.

- **Run in current directory**:
  ```bash
  cd ~/my-project
  nova task plan "Review the README"
  ```
  Nova will use `~/my-project` as its workspace.

- **Run in Sandbox**:
  ```bash
  nova sandbox build "Create a new project"
  ```
  Nova will use `~/.nova/sandbox` as its workspace.

## Troubleshooting
If `nova` is not found after installation:
- Ensure your Python scripts directory (e.g., `~/.local/bin` or Python framework bin) is in your `PATH`.
- Try uninstalling and reinstalling: `pip uninstall nova-agent-cli && pip install .`

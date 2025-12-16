# 🚀 Nova Agent CLI - Quick Start Guide

## What is Nova?
**Nova** is a complete local AI agent CLI powered by Ollama. It can execute file operations, run shell commands, fetch web content—all through a beautiful terminal interface with MCP-style tools.

---

## 📍 Project Location
```bash
/Users/chepuriharikiran/Desktop/github/nova-agent-cli/
```

---

## ⚡ Quick Start (Choose One)

### Option 1: Docker (Recommended ✓)
```bash
cd /Users/chepuriharikiran/Desktop/github/nova-agent-cli

# Start Nova
./scripts/run_docker.sh

# Chat with Nova
docker compose exec nova-agent nova
```

### Option 2: Local Python
```bash
cd /Users/chepuriharikiran/Desktop/github/nova-agent-cli

# Install (one-time)
./scripts/install.sh

# Run Nova
./scripts/run_local.sh
```

> **Note**: Your Python is 3.8.18. Scripts require 3.11+. Docker setup avoids this issue.

---

## 💬 Example Commands

### Interactive Chat
```bash
nova

You > Create a file hello.py that prints "Hello World"
You > Now run that file
You > List files in the workspace
You > Fetch https://example.com
```

### One-Shot Mode
```bash
nova -c "What files are in my workspace?"
nova -c "Create a todo list in todos.txt"
nova -m llama3.1:8b  # Use different model
```

---

## 🛠️ Available Tools

- **file.read** - Read files from workspace
- **file.write** - Write files to workspace  
- **shell.run** - Execute safe commands (ls, cat, python, git, etc.)
- **web.get** - Fetch content from URLs

All file operations are sandboxed to `workspace/` directory for safety.

---

## 🔧 Configuration

Edit `.env` file:
```bash
OLLAMA_MODEL=llama3              # Change model
OLLAMA_BASE_URL=http://...       # Ollama location
ALLOW_SHELL_COMMANDS=true        # Enable/disable shell
SHELL_COMMAND_ALLOWLIST=ls,cat...  # Add more commands
```

---

## 🐳 Docker Commands

```bash
# Start
./scripts/run_docker.sh

# Chat
docker compose exec nova-agent nova

# Stop
docker compose down

# View logs
docker compose logs -f nova-agent

# Rebuild
docker compose up --build
```

---

## 🐛 Troubleshooting

### Ollama Not Reachable
```bash
# Check Ollama is running
curl http://127.0.0.1:11434/api/tags

# Start Ollama if needed
ollama serve

# Pull model
ollama pull llama3
```

### Docker Can't Reach Ollama
1. Check `.env` has: `OLLAMA_BASE_URL=http://host.docker.internal:11434`
2. Ensure Ollama is running on host

### Python Version (Local Setup)
```bash
# Install Python 3.11+
brew install python@3.11

# Or use Docker (no Python version issues)
```

---

## 📚 Files Overview

```
nova-agent-cli/
├── src/
│   ├── nova_cli.py         # CLI entry point
│   └── agent_core/
│       ├── config.py       # Configuration
│       ├── model_client.py # Ollama client
│       ├── tools.py        # MCP tools
│       └── agent_loop.py   # Agent engine
├── scripts/
│   ├── install.sh          # Local install
│   ├── run_local.sh        # Run locally
│   └── run_docker.sh       # Run with Docker
├── workspace/              # Your files (sandboxed)
├── docker-compose.yml      # Docker config
├── .env.example           # Config template
└── README.md              # Full documentation
```

---

## ✨ Your Available Models

You already have these models pulled:
- **llama3:latest** (default)
- **llama3.1:8b** (newer, recommended)
- **qwen2:7b-instruct** (fast)
- **deepseek-coder-v2** (coding specialist)
- Plus others!

Switch models:
```bash
nova -m llama3.1:8b
# or edit .env: OLLAMA_MODEL=llama3.1:8b
```

---

## 🎯 Try These Examples

1. **File Creation**
   ```
   You > Create a Python script fibonacci.py that generates fibonacci numbers
   ```

2. **Research**
   ```
   You > Fetch the Hacker News homepage and summarize the top stories
   ```

3. **Development**
   ```
   You > Create a package.json for a Node.js project
   You > List all Python files in the workspace
   ```

4. **Multi-Step Tasks**
   ```
   You > Create a README.md, then read it back to me
   ```

---

## 🔒 Safety Features

- ✓ Workspace sandboxing (file operations only in `workspace/`)
- ✓ Command allowlisting (only safe commands execute)
- ✓ Destructive pattern blocking (`rm -rf`, etc. blocked)
- ✓ Timeout enforcement (30s max)
- ✓ Local-only (no external API calls except web.get)

---

## 📖 More Information

- **Full docs**: See `README.md` in project directory
- **Implementation details**: See `walkthrough.md` artifact
- **Add new tools**: Edit `src/agent_core/tools.py`

---

**Nova is ready! Start chatting with your local AI agent. 🚀**

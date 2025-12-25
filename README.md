# Nova Agent CLI v2.0 🚀

**Nova is an industrial-grade, local-first autonomous AI agent designed for power users.** It prioritizes privacy, uncensored operation, and "clean and work it perfect" reliability. Nova interacts with the user through a highly aesthetic, Cyberpunk-themed Terminal User Interface (TUI) and uses a sophisticated ReAct (Reason-Act-Observe) loop to execute complex tasks autonomously.

Unlike cloud agents, Nova runs fully on your machine with Ollama, giving you:
✔ **Near-zero latency** – Local inference with no network round-trips
✔ **Zero API cost** – Run 7B–70B+ models locally
✔ **Zero data exfiltration** - Your code never leaves your device

---

## 🎯 Who Nova Is For

Nova is built for:
- 🧑‍💻 **Software Engineers** – Refactoring, debugging, and code generation
- 🔧 **DevOps / SREs** – Docker management, CI/CD, and infra automation
- 🧪 **Researchers** – Local experimentation without data leaks
- 🏴‍☠️ **Power Users** – Uncensored local models and full system access
- 🧠 **Agent Builders** – Extendable ReAct loop + tool orchestration

## ✨ Key Features

- **🧠 Agentic Intelligence**: Advanced ReAct loop for complex problem-solving and autonomous debugging.
- **⚡ Turbo Mode**: Multi-threaded tool execution for maximum performance.
- **🐳 Cloud-Ready Docker**: Deploy as a full stack (Agent + Ollama) anywhere.
- **🕵️ 100% Private**: No telemetry, no external API calls.
- **🖥️ Cyberpunk TUI**: A highly aesthetic, interactive terminal interface with real-time Plan Tree visualization.
- **📚 Local Knowledge**: Integrated ChromaDB vector store for long-term memory.
- **🛠️ Agent Developer Kit (ADK)**: Extensible toolkit for adding custom capabilities.

## 🧠 Agent Architecture

Nova operates using an enhanced **ReAct (Reason → Act → Observe)** loop:

1. **Reason** – Analyze the task and plan steps based on available tools.
2. **Act** – Invoke tools (read code, run shell commands, manage Docker).
3. **Observe** – Validate outputs, logs, and errors from the action.
4. **Iterate** – Refine the plan until the task is complete.

This loop enables:
- Multi-step problem solving
- Autonomous debugging
- Self-verification of results

At a high level: `User` → `Planner` → `Tool Executor` → `Verifier` → `Memory` → `Response`

## 🛡️ Safety & Control

Nova is **uncensored by default**, but **not unsafe**.

- 🚧 **Sandbox Mode**: Isolates risky operations in a controlled environment.
- 🔐 **Security Mode**: Enables strict command filtering for shell operations.
- 👤 **User-in-the-loop**: Ask for permission before executing sensitive actions.
- 🧪 **Dry-Run**: Verify infrastructure changes before applying them.

**Nova does not bypass OS-level permissions or system security — it operates strictly within user-granted access.**

> **Power is opt-in. Safety is configurable.**

## ☁️ Why Not Cloud Agents?

Cloud agents introduce:
- Latency from network hops
- Ongoing token costs
- Implicit data exposure
- Vendor lock-in

Nova eliminates all four by design.

## 🚫 Non-Goals

Nova is not:
- A general-purpose chatbot
- A SaaS product
- A replacement for IDEs

Nova is a **local autonomous execution agent**.

## 🚀 Quick Start

### Option 1: Docker (Recommended)
> Requires Docker + Docker Compose (GPU optional).

```bash
git clone https://github.com/chepuriharikiran/nova
cd nova
docker compose up -d
docker exec -it nova_agent nova ui
```

✔ Includes Ollama + Uncensored Model
✔ GPU auto-detected
✔ Persistent model cache

> 💡 **CPU-only users:** Nova works fine on CPU, just expect slower responses compared to GPU acceleration.

### Option 2: Local Installation
1. **Prerequisites**: [Ollama](https://ollama.com) installed and running.
2. **Install Nova**:
   ```bash
   pip install -e .
   ```
3. **Pull Core Model**:
   ```bash
   ollama pull mannix/llama3.1-8b-abliterated
   ```

## 🧪 Example Tasks Nova Can Handle

**Coding & Refactoring**
```bash
nova task run "
Analyze this repository,
identify performance bottlenecks,
refactor the slowest module,
write unit tests,
and verify everything passes
"
```

**DevOps Automation**
```bash
nova sandbox build "
Create a FastAPI app with JWT auth,
Dockerize it,
and generate a README
"
```

**Security Auditing**
```bash
nova run "Scan my Docker setup and suggest security hardening"
```

## 🛠️ Configuration

Nova is configured via `.env` file or environment variables.

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_PROVIDER` | `ollama` | Core AI provider (ollama, gemini) |
| `OLLAMA_MODEL` | `mannix/llama3.1...` | The uncensored local model |
| `TURBO_MODE` | `true` | Enable parallel tool execution (8 workers) |
| `SECURITY_MODE` | `false` | Enable strict safety checks |
| `ANONYMIZED_TELEMETRY` | `False` | **Strictly disabled** for privacy |

## 🛣️ Roadmap

- [ ] Persistent agent memory (vector store upgrades)
- [ ] GitHub Actions integration
- [ ] Multi-agent collaboration
- [ ] Web UI dashboard
- [ ] Fine-grained tool permissions
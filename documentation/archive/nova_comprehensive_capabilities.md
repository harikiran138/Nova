> **ARCHIVED**: Superseded by [Project_Overview.md](../Project_Overview.md) on 2025-12-25.

# Nova v2.2 - Comprehensive Capabilities & Feature Report

## 1. Core Architecture

Nova v2.2 is an autonomous, local-first AI agent designed for privacy and flexibility. It operates on a modular architecture comprising:

*   **Agent Core**: The central brain managing the agent loop, tool execution, and memory.
*   **Planner**: A specialized module that breaks down complex user goals into structured plans with specific steps, assigning roles (Coder, Researcher, Reviewer) and tools to each step.
*   **Memory System**: A persistent JSON-based memory system that stores session history and "learned facts" about the user and environment.
*   **RAG Engine**: A Retrieval-Augmented Generation system using ChromaDB to index and retrieve context from the local workspace.
*   **Safety Layer**: A robust safety policy engine enforcing permissions (Read-Only, Sandbox, Restricted, Unrestricted) and auditing all actions.

## 2. Agent Profiles

Nova supports specialized personas, configurable via `profiles.yaml`:

*   **General**: A versatile assistant with empathy and active listening traits. Access to most tools.
*   **Coder**: A software engineering specialist. Default sandbox enabled. Focused on file operations, git, and code search.
*   **Researcher**: Focused on information gathering. Access to web search, arXiv, and weather tools.

## 3. Tool Ecosystem

Nova possesses a rich set of tools registered in `src/agent_core/tools/registry.py`.

### 3.1 File System Operations (`file.*`)
*   `file.read(path)`: Read file content.
*   `file.write(path, content)`: Write content to a file.
*   `file.list(path)`: List directory contents.
*   `file.mkdir(path)`: Create directories.
*   `file.move(src, dst)`: Move files/directories.
*   `file.copy(src, dst)`: Copy files/directories.
*   `file.delete(path)`: Delete files/directories.
*   **Feature**: Sandbox-aware. In sandbox mode, operations are restricted to the sandbox directory.

### 3.2 Git Integration (`git.*`)
*   `git.status()`: Check repository status.
*   `git.diff()`: View changes.
*   `git.log(n)`: View commit history.
*   `git.commit(message)`: Commit changes.
*   `git.add(files)`: Stage files.

### 3.3 Shell & System (`shell.*`, `sys.*`)
*   `shell.run(command)`: Execute shell commands.
*   `shell.run_safe(command)`: Execute with safety checks.
*   `shell.list()`: List running processes.
*   `shell.kill(pid)`: Terminate a process.
*   `sys.netinfo()`: Get network interface details.
*   `sys.open(path)`: Open a file with the default OS application.
*   `sys.usage()`: CPU and RAM usage.
*   `sys.osinfo()`: OS details.
*   `sys.disk_usage()`: Disk space info.

### 3.4 Network & Web (`net.*`, `web.*`)
*   `net.get(url)`: HTTP GET request.
*   `net.post(url, data)`: HTTP POST request.
*   `net.download(url, filepath)`: Download files.
*   `net.check()`: Check internet connectivity.
*   `web.search(query)`: Search DuckDuckGo.
*   `arxiv(query)`: Search arXiv papers.
*   `crypto_price(coin_id)`: Get crypto prices (CoinGecko).
*   `weather_forecast(location)`: Get weather (wttr.in).

### 3.5 Kali Linux Security Tools (`kali.*`)
*   **Requirement**: Docker.
*   `kali.start_session()`: Start a persistent Kali container.
*   `kali.stop_session()`: Stop the session.
*   `kali.run(command)`: Run any command in Kali.
*   `kali.install(packages)`: Install tools via apt.
*   `kali.nmap(target)`: Network scanning.
*   `kali.sqlmap(url)`: SQL injection testing.
*   `kali.nikto(host)`: Web server scanning.
*   `kali.msf(command)`: Metasploit Framework interaction.
*   `kali.dnsmasq(args)`: DNS server and resolver.
*   `kali.ettercap(args)`: SSL/TLS MITM tool.
*   `kali.faraday(args)`: Web application security testing framework.
*   `kali.hashcat(args)`: Password cracking tool.
*   `kali.maltego(args)`: Open-source intelligence gathering tool.

### 3.6 Local Utilities (`local_tools.*`)
*   `password_generator(length, use_symbols)`: Generate strong passwords.
*   `regex_tester(pattern, text)`: Test regex patterns.
*   `zip_unzip(action, path, output)`: Compress or extract archives.
*   `file_convert(input, output_format)`: Convert data files (e.g., CSV to JSON).
*   `unit_converter`: Simple unit conversion (stub).

### 3.7 API Interaction (`api.*`)
*   `api.request(method, url, headers, data)`: Generic HTTP client. Supports environment variable injection in headers (e.g., `Authorization: Bearer $API_KEY`).

### 3.8 Memory (`memory.*`)
*   `memory.remember(fact)`: Store a fact for future sessions.
*   `memory.recall()`: Retrieve learned facts.

## 4. Safety & Security

*   **Audit Logging**: All tool executions are logged to `~/.nova/audit.log`.
*   **Sandbox Mode**: Restricts file and shell operations to a safe directory.
*   **Dangerous Command Blocking**: Prevents execution of high-risk commands (e.g., `rm -rf /`, `mkfs`) unless explicitly allowed.

## 5. Configuration

*   **Environment**: Loaded from `.env` files.
*   **Model Support**: Ollama (local), Gemini, OpenRouter.
*   **Offline Mode**: Can be toggled to prevent external network requests.

### 3.9 System Tools Availability
*   **Available via `shell.run`**: `curl`, `tar`, `git`, `python3`, `ruby`, `node`, `sqlite3`.
*   **Note**: `wget` is not installed by default (use `curl -O`). `rsyslog` and `psad` are typically Linux-specific and may not be available on macOS without installation.

#!/usr/bin/env python3
"""Nova Agent CLI - Main entry point."""

import sys
import time
from pathlib import Path
import click
from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.markdown import Markdown
from rich.table import Table

# Neural Glass Aesthetic Theme
neural_theme = Theme({
    "nova": "bold #00F5FF",        # Neon Cyan
    "accent": "#8B5CF6",           # Neon Violet
    "success": "#22C55E",          # Signal Green
    "error": "#EF4444",            # Alert Red
    "info": "#00F5FF dim",         # Muted Cyan
    "dim": "#6B7280",              # Muted Gray
    "user": "bold #8B5CF6",        # User prompt accent
    "prompt.path": "#6B7280",
    "prompt.nova": "#00F5FF",
    "prompt.arrow": "#8B5CF6"
})

console = Console(theme=neural_theme, width=100)

# Core Imports
from src.nova_shared.config import Config
from src.nova_ai.model_client import OllamaClient
from src.nova_agents.agent_loop import AgentLoop
from src.nova_agents.tools.registry import ToolRegistry

def get_client(config: Config):
    """Get the appropriate model client based on config."""
    if config.model_provider == "gemini":
        from src.nova_ai.model_client import GeminiClient
        return GeminiClient(config.gemini_api_key, config.gemini_model)
    return OllamaClient(config.ollama_base_url, config.ollama_model)

def print_welcome(config: Config, client):
    """Print welcome message with configuration info."""
    import random
    from src.nova_agents.tools.registry import ToolRegistry
    
    tips = [
        "Type /help to see available commands.",
        "Use 'nova sandbox build' for safe experiments.",
        "Nova can remember your sessions! Use 'nova history'.",
        "Try 'nova code' for specialized coding tasks.",
        "Privacy First: All actions are local unless you approve network access."
    ]
    tip = random.choice(tips)

    # Get actual tool count
    registry = ToolRegistry(config.workspace_dir, sandbox_mode=config.security_mode)
    tool_count = len(registry.tools)
    
    # Premium Welcome Banner - Cyberpunk Clean
    banner = f"""
[nova]╭────────────────────────────────────────────────────────────╮[/nova]
[nova]│[/nova]  [bold #00F5FF]✨ Nova[/bold #00F5FF] — [accent]Autonomous Local Intelligence[/accent]          [nova]│[/nova]
[nova]│[/nova]  [dim]No cloud. No tracking. Pure local cognition.[/dim]           [nova]│[/nova]
[nova]├────────────────────────────────────────────────────────────┤[/nova]
[nova]│[/nova]  [success]•[/success] [bold]Identity:[/bold]  Nova v3.5 (Neural Glass)              [nova]│[/nova]
[nova]│[/nova]  [success]•[/success] [bold]Status:[/bold]    [success]ONLINE[/success] ([info]{config.safety_level.upper()}[/info])         [nova]│[/nova]
[nova]│[/nova]  [success]•[/success] [bold]Ecosystem:[/bold] {tool_count} cognitive tools available     [nova]│[/nova]
[nova]│[/nova]  [success]•[/success] [bold]Workspace:[/bold] [dim]{config.workspace_dir.name}/...[/dim]               [nova]│[/nova]
[nova]╰────────────────────────────────────────────────────────────╯[/nova]
    """
    console.print(banner)
    console.print(f"[dim]Tip: {tip}[/dim]\n")


def select_model(client, config: Config) -> str:
    """Interactive model selection."""

    # Ollama Logic
    console.print("[dim]Accessing neural models...[/dim]")
    models = client.get_available_models()
    
    if not models:
        console.print("[error]✖ No cognitive models found.[/error]")
        return client.model
    
    table = Table(title="Neural Model Inventory", border_style="accent")
    table.add_column("#", style="info", justify="right")
    table.add_column("Model Identifier", style="nova")
    
    for idx, model in enumerate(models, 1):
        table.add_row(str(idx), model)
    
    console.print(table)
    
    choices = [str(i) for i in range(1, len(models) + 1)]
    try:
        selection = IntPrompt.ask("[nova]Select model ID[/nova]", choices=choices)
        selected_model = models[selection - 1]
        console.print(f"[success]✔ Switched to {selected_model}[/success]")
        return selected_model
    except (ValueError, IndexError):
        console.print("[error]✖ Invalid neural mapping.[/error]")
        return client.model


def handle_slash_command(command: str, agent: AgentLoop, client, config: Config) -> str:
    """Handle slash commands. Returns action: 'exit', 'reload', 'continue'."""
    cmd_parts = command.strip().split()
    cmd = cmd_parts[0].lower()
    
    if cmd in ['/quit', '/exit']:
        console.print("[dim]Goodbye! 👋[/dim]")
        return "exit"
        
    elif cmd == '/clear':
        agent.reset_conversation()
        return "continue"
        
    elif cmd == '/model':
        new_model = select_model(client, config)
        if new_model != client.model:
            config.ollama_model = new_model
            client.model = new_model
            console.print(f"[green]Switched to {new_model}[/green]")
            return "reload"
        return "continue"

    elif cmd == '/help':
        help_text = """
# Available Commands

- `/model`: Change model for current provider (Ollama)
- `/clear`: Clear conversation history
- `/info`: Show current session configuration
- `/help`: Show this help message
- `/quit`: Exit the application
        """
        console.print(Markdown(help_text))
        return "continue"
        
    elif cmd == '/info':
        print_welcome(config, client)
        return "continue"
        
    else:
        import difflib
        available_commands = ['/model', '/clear', '/info', '/help', '/quit', '/exit']
        matches = difflib.get_close_matches(cmd, available_commands, n=1, cutoff=0.6)
        
        console.print(f"[red]Unknown command: {cmd}[/red]")
        if matches:
            console.print(f"[yellow]Did you mean [bold]{matches[0]}[/bold]?[/yellow]")
        return "continue"


def run_interactive(config: Config, profile_name: str = "general", sandbox_mode: bool = False):
    """Run the agent in interactive mode."""
    
    # Initial Setup
    client = get_client(config)
    
    # Startup Animation
    from src.utils.animations import run_system_scan
    if not config.skip_animations:
        console.print("[dim]Initializing Nova Core...[/dim]")
        run_system_scan(duration=2)
    
    print_welcome(config, client)

    tools = ToolRegistry(
        workspace_dir=config.workspace_dir,
        allow_shell=config.allow_shell_commands,
        shell_allowlist=config.shell_command_allowlist,
        offline_mode=config.offline_mode,
        sandbox_mode=sandbox_mode
    )
    
    # Status Handler
    spinner = None
    def status_handler(event, *args):
        nonlocal spinner
        if event == "thinking_start":
            if not spinner:
                spinner = console.status("[info]Nova is thinking...[/info]", spinner="dots12")
                spinner.start()
        elif event == "thinking_end":
            if spinner:
                spinner.stop()
                spinner = None
        elif event == "tool_start":
            if spinner: spinner.stop()
            tool_name, tool_args = args
            console.print(f"[dim]  ℹ Executing: {tool_name}[/dim]")
            if spinner: spinner.start()
        elif event == "tool_end":
            if spinner: spinner.stop()
            tool_name, result = args
            if result["success"]:
                console.print(f"  [success]✔[/success] [bold]{tool_name}[/bold]: [dim]Action confirmed[/dim]")
                # Optionally show small output if relevant, but keep it clean
            else:
                console.print(f"  [error]✖[/error] [error]{tool_name}[/error]: {result.get('error', 'Critical failure')}")
            if spinner: spinner.start()

    # Stream Handler
    def stream_handler(chunk):
        if chunk:
            console.print(chunk, end="")

    agent = AgentLoop(client, tools, profile_name=profile_name, sandbox_mode=sandbox_mode, status_callback=status_handler, stream_callback=stream_handler)
    
    while True:
        try:
            # Custom prompt styling
            path = Path.cwd().name
            prompt_header = f"[prompt.nova]╭─ nova@core[/prompt.nova] [dim]▸[/dim] [prompt.path]~/{path}[/prompt.path]"
            console.print(prompt_header)
            user_input = console.input("[prompt.nova]╰─[/prompt.nova] [prompt.arrow]❯[/prompt.arrow] ").strip()
            
            if not user_input:
                continue
                
            if user_input.startswith("/"):
                action = handle_slash_command(user_input, agent, client, config)
                if action == "exit":
                    break
                elif action == "reload":
                    client = get_client(config)
                    agent = AgentLoop(client, tools, profile_name=profile_name, sandbox_mode=sandbox_mode, status_callback=status_handler, stream_callback=stream_handler)
                    print_welcome(config, client)
                continue
            
            if user_input.lower() in ['exit', 'quit']:
                console.print("[dim]Disconnecting...[/dim]")
                break
            
            console.print(f"\n[nova]Nova[/nova] [dim]▸[/dim] ", end="")
            response = agent.process_input(user_input)
            
            if spinner: spinner.stop()
            if not response:
                console.print("[red]No response from agent.[/red]")
            console.print() # Ensure newline after response
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")



def get_telemetry_snapshot(config: Config):
    from src.nova_ops.telemetry import TelemetryManager
    tm = TelemetryManager(config.workspace_dir / ".nova" / "telemetry.json")
    # Return raw metrics for easier calculation
    return tm.metrics.copy()

def print_performance_summary(start_metrics: dict, end_metrics: dict, duration: float):
    """Print a sleek performance summary of the session."""
    
    # Calculate Deltas
    tokens_used = end_metrics.get("total_tokens", 0) - start_metrics.get("total_tokens", 0)
    cost = end_metrics.get("total_cost", 0.0) - start_metrics.get("total_cost", 0.0)
    
    # Don't show if empty run
    if tokens_used == 0 and cost == 0:
        return

    summary = Table(box=None, show_header=False, padding=(0, 2))
    summary.add_column("Metric", style="dim")
    summary.add_column("Value", style="bold cyan")
    
    summary.add_row("⏱ Duration", f"{duration:.2f}s")
    summary.add_row("🪙 CostEstimate", f"${cost:.4f}")
    summary.add_row("💎 Tokens", f"{tokens_used}")
    
    console.print()
    console.print(Panel(summary, title="[info]Performance Stats[/info]", border_style="dim", expand=False))


def run_oneshot(config: Config, command: str):
    """Run a single command and exit."""
    # Initialize components
    client = get_client(config)
    tools = ToolRegistry(
        workspace_dir=config.workspace_dir,
        allow_shell=config.allow_shell_commands,
        shell_allowlist=config.shell_command_allowlist,
        offline_mode=config.offline_mode,
        sandbox_mode=config.security_mode
    )
    agent = AgentLoop(client, tools)
    
    # Test connection
    if not client.test_connection():
        console.print(f"[red]✗ Cannot connect to {config.model_provider}[/red]")
        sys.exit(1)
    
    # Process command
    try:
        console.print(f"[bold blue]You:[/bold blue] {command}\n")
        
        # Performance Tracking
        start_metrics = get_telemetry_snapshot(config)
        start_time = time.time()
        
        response = agent.process_input(command)
        
        end_time = time.time()
        end_metrics = get_telemetry_snapshot(config)
        
        if response:
            console.print("\n[bold green]Nova:[/bold green]")
            console.print(Panel(Markdown(response), border_style="green", padding=(1, 2)))
            
            # Print Summary
            print_performance_summary(start_metrics, end_metrics, end_time - start_time)
        else:
            console.print("[red]Failed to get response.[/red]")
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error during execution: {e}[/red]")
        sys.exit(1)


from src.nova_agents.planner import Planner
from src.nova_ops.sandbox import Sandbox

def run_task_command(config: Config, args):
    """Handle task commands."""
    client = get_client(config)
    tools = ToolRegistry(
        workspace_dir=config.workspace_dir,
        allow_shell=config.allow_shell_commands,
        shell_allowlist=config.shell_command_allowlist,
        offline_mode=config.offline_mode,
        sandbox_mode=args.sandbox if args.sandbox is not None else config.security_mode
    )
    
    try:
        if args.task_action == "plan":
            planner = Planner(client, tools)
            console.print(f"[bold]Planning task:[/bold] {args.goal}")
            task = planner.plan_task(args.goal)
            
            console.print("\n[bold]Generated Plan:[/bold]")
            for step in task.steps:
                tool_info = f" (via {step.tool})" if step.tool else ""
                console.print(f"{step.id}. {step.description}{tool_info}")
                
        elif args.task_action == "run":
            planner = Planner(client, tools, profile_name=args.agent or "general")
            agent = AgentLoop(client, tools, profile_name=args.agent or "general", sandbox_mode=args.sandbox)
            
            console.print(f"[bold]Planning task:[/bold] {args.goal}")
            task = planner.plan_task(args.goal)
            
            console.print("\n[bold]Executing Plan...[/bold]")
            agent.run_task(task)
    except Exception as e:
        console.print(f"[red]Task execution failed: {e}[/red]")
        sys.exit(1)

def list_tools(config: Config):
    """List available tools."""
    tools = ToolRegistry(
        workspace_dir=config.workspace_dir,
        allow_shell=config.allow_shell_commands,
        shell_allowlist=config.shell_command_allowlist,
        offline_mode=config.offline_mode,
        sandbox_mode=config.security_mode
    )
    
    console.print(Panel(tools.get_tool_descriptions(), title="Available Tools", border_style="blue"))


def run_sandbox_command(config: Config, args):
    """Handle sandbox commands."""
    sandbox = Sandbox()
    
    if args.sandbox_action == "init":
        sandbox.init()
    elif args.sandbox_action == "clean":
        sandbox.clean()
    elif args.sandbox_action == "info":
        console.print(sandbox.get_info())
    elif args.sandbox_action == "build":
        # Ensure sandbox exists
        sandbox.init()
        
        # Override workspace to sandbox
        config.workspace_dir = sandbox.path
        
        # Run task in sandbox
        client = get_client(config)
        tools = ToolRegistry(
            workspace_dir=config.workspace_dir,
            allow_shell=config.allow_shell_commands,
            shell_allowlist=config.shell_command_allowlist,
            sandbox_mode=True
        )
        # Sandbox build implies sandbox mode and likely coder profile if not specified
        profile = args.agent or "coder"
        planner = Planner(client, tools, profile_name=profile)
        agent = AgentLoop(client, tools, profile_name=profile, sandbox_mode=True)
        
        console.print(f"[bold]Building in Sandbox:[/bold] {args.goal}")
        task = planner.plan_task(args.goal)
        
        console.print("\n[bold]Executing Build Plan...[/bold]")
        agent.run_task(task)

def list_agents(config: Config):
    """List available agent profiles."""
    profiles = config.load_profiles()
    
    table = Table(title="Available Agents")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Tools", style="green")
    
    for name, profile in profiles.items():
        tools = ", ".join(profile.get("allowed_tools", ["*"]))
        table.add_row(name, profile.get("description", ""), tools)
        
    console.print(table)

def show_status(config: Config, args):
    """Show current status."""
    status_info = f"""
[nova]Nova System Protocol[/nova]
────────────────────────────────────────
[bold]Provider:[/bold]  [info]Ollama[/info]
[bold]Model:[/bold]     [accent]{config.ollama_model}[/accent]
[bold]Workspace:[/bold] [dim]{config.workspace_dir}[/dim]
[bold]Security:[/bold]  [success]{'Enhanced Sandbox' if args.sandbox else 'Standard'}[/success]
[bold]Profile:[/bold]   [nova]{args.agent or 'general'}[/nova]
"""
    console.print(Panel(status_info, title="[accent]System Metrics[/accent]", border_style="accent", expand=False))

@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--agent", "-a", default="general", help="Agent profile")
@click.option("--sandbox/--no-sandbox", default=None, help="Sandbox mode")
def cli(ctx, agent, sandbox):
    """Nova Agent CLI"""
    if ctx.invoked_subcommand is None:
        config = Config.from_env()
        run_interactive(config, profile_name=agent, sandbox_mode=sandbox or False)

@cli.command()
@click.argument("goal")
@click.option("--agent", "-a", default="general")
@click.option("--sandbox/--no-sandbox", default=None)
@click.option("--resume", "-r", default=None)
def run(goal, agent, sandbox, resume):
    """Execute a goal."""
    config = Config.from_env()
    client = get_client(config)
    if sandbox is None:
        profiles = config.load_profiles()
        sandbox = profiles.get(agent, {}).get("default_sandbox", False)

    tools = ToolRegistry(config.workspace_dir, config.allow_shell_commands, config.shell_command_allowlist, offline_mode=config.offline_mode, sandbox_mode=sandbox)

    agent_loop = AgentLoop(client, tools, profile_name=agent, sandbox_mode=sandbox)
    
    if resume:
        if not agent_loop.load_session(resume):
            return

    # Track Performance
    start_metrics = get_telemetry_snapshot(config)
    start_time = time.time()
    
    try:
        if config.reasoning_mode == "planner":
            console.print("[bold cyan]🧠 PVEV Reasoning Mode Activated[/bold cyan]")
            agent_loop.execute_pvev_session(goal)
        else:
            agent_loop.process_input(goal)
            
    finally:
        # Show stats even if it crashes
        end_time = time.time()
        end_metrics = get_telemetry_snapshot(config)
        print_performance_summary(start_metrics, end_metrics, end_time - start_time)

@cli.command()
def history():
    """Show session history."""
    config = Config.from_env()
    from src.nova_ai.memory import MemoryManager
    memory = MemoryManager(config.workspace_dir / ".nova" / "memory")
    sessions = memory.list_sessions()
    
    if not sessions:
        console.print("No history found.")
        return
        
    table = Table(title="Nova Session History", border_style="accent")
    table.add_column("Session ID", style="info")
    table.add_column("Timestamp", style="dim")
    table.add_column("Last Context", style="white")
    
    for s in sorted(sessions, key=lambda x: x['timestamp'], reverse=True):
        ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(s['timestamp']))
        table.add_row(s['id'], ts, s['preview'])
    console.print(table)

@cli.command()
@click.argument("name", required=False)
def mode(
    name: str,
):
    """Switch Nova's operational mode."""
    from src.utils.env_manager import EnvManager
    
    modes = {
        "autonomy": {
            "NOVA_OFFLINE_MODE": "false",
            "ENABLE_AUTONOMOUS_INSTALL": "true",
            "ENABLE_AUTO_MODEL_SWITCH": "true",
            "SECURITY_MODE": "false",
            "TURBO_MODE": "false",
            "SAFETY_LEVEL": "unrestricted"
        },
        "security": {
            "NOVA_OFFLINE_MODE": "true",
            "ENABLE_AUTONOMOUS_INSTALL": "false",
            "ENABLE_AUTO_MODEL_SWITCH": "false",
            "SECURITY_MODE": "true",
            "TURBO_MODE": "false",
            "SAFETY_LEVEL": "sandbox_only"
        },
        "turbo": {
            "NOVA_OFFLINE_MODE": "true",
            "ENABLE_AUTONOMOUS_INSTALL": "false",
            "ENABLE_AUTO_MODEL_SWITCH": "false",
            "SECURITY_MODE": "true",
            "TURBO_MODE": "true",
            "SAFETY_LEVEL": "restricted",
            "MODEL_PROVIDER": "ollama"
        },
        "balanced": {
            "NOVA_OFFLINE_MODE": "false",
            "ENABLE_AUTONOMOUS_INSTALL": "true",
            "ENABLE_AUTO_MODEL_SWITCH": "true",
            "SECURITY_MODE": "false",
            "TURBO_MODE": "false",
            "SAFETY_LEVEL": "restricted"
        }
    }

    if not name:
        console.print("[bold cyan]Available Modes:[/bold cyan]")
        for m in modes:
            console.print(f" - {m}")
        return

    if name not in modes:
        console.print(f"[bold red]Unknown mode:[/bold red] {name}")
        return

    env_manager = EnvManager(Path.cwd() / ".env")
    env_manager.update(modes[name])
    console.print(f"[bold green]Switched to {name.capitalize()} Mode.[/bold green]")

@cli.command()
def dashboard():
    """Launch the real-time Agent Dashboard."""
    from src.ui.dashboard import Dashboard
    try:
        dash = Dashboard()
        dash.run()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Dashboard closed.[/bold yellow]")

@cli.command(name="self-analyze")
def self_analyze():
    """Perform self-analysis and show capabilities."""
    config = Config.from_env()
    
    console.print(Panel("[bold cyan]Nova Self-Analysis Protocol Initiated[/bold cyan]", border_style="cyan"))
    
    # 1. Tool Analysis
    from src.nova_agents.tools.registry import ToolRegistry
    tools = ToolRegistry(
        workspace_dir=config.workspace_dir,
        allow_shell=config.allow_shell_commands,
        shell_allowlist=config.shell_command_allowlist,
        offline_mode=config.offline_mode,
        sandbox_mode=config.security_mode
    )
    
    console.print("\n[bold]1. Tool Ecosystem Analysis[/bold]")
    console.print(f"Detected {len(tools.tools)} registered tools.")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Tool Name", style="cyan")
    table.add_column("Description", style="white")
    
    for name, tool in tools.tools.items():
        table.add_row(name, tool.description.split('\n')[0][:80])
        
    console.print(table)
    
    # 2. Telemetry Report
    console.print("\n[bold]2. Performance Telemetry[/bold]")
    from src.nova_ops.telemetry import TelemetryManager
    tm = TelemetryManager(config.workspace_dir / ".nova" / "telemetry.json")
    stats = tm.get_stats()
    
    t_table = Table(show_header=False, box=None)
    t_table.add_column("Metric", style="dim")
    t_table.add_column("Value", style="bold green")
    
    t_table.add_row("Success Rate", stats["success_rate"])
    t_table.add_row("Total Tasks", str(stats["total_tasks"]))
    
    tokens = stats.get("tokens", {})
    t_table.add_row("Total Tokens", str(tokens.get("total", 0)))
    t_table.add_row("Est. Cost", stats.get("cost", "$0.0000"))
    
    cache = stats.get("cache", {})
    hits = cache.get("hits", 0)
    misses = cache.get("misses", 0)
    total_reqs = hits + misses
    hit_rate = f"{(hits/total_reqs*100):.1f}%" if total_reqs > 0 else "0.0%"
    t_table.add_row("Cache Hit Rate", hit_rate)
    
    console.print(t_table)

    # 3. Capabilities Report
    console.print("\n[bold]3. Comprehensive Capabilities Report[/bold]")
    doc_path = Path(__file__).parent.parent / "documentation" / "nova_comprehensive_capabilities.md"
    
    if doc_path.exists():
        console.print(f"[dim]Loading report from {doc_path}[/dim]")
        md_content = doc_path.read_text()
        console.print(Markdown(md_content))
    else:
        console.print("[yellow]Capabilities report not found. Generating summary...[/yellow]")
        # Fallback summary
        summary = """
        ## Core Capabilities
        - **Autonomous Planning**: Breaks down complex goals into steps.
        - **Local Execution**: Runs entirely on your machine.
        - **Tool Use**: File manipulation, shell execution, web search (if allowed).
        - **Memory**: Remembers past sessions and learned facts.
        """
        console.print(Markdown(summary))
        
    console.print("\n[bold green]Self-Analysis Completed Successfully.[/bold green]")

@cli.command()
def ui():
    """Launch TUI."""
    config = Config.from_env()
    from src.ui.nova_tui import NovaApp
    app = NovaApp(config)
    app.run()

@cli.group()
def sandbox():
    """Sandbox management."""
    pass

@sandbox.command(name="build")
@click.argument("goal")
@click.option("--agent", "-a", default="coder")
def sandbox_build(goal, agent):
    """Build in sandbox."""
    config = Config.from_env()
    from src.nova_ops.sandbox import Sandbox
    from src.nova_agents.planner import Planner
    
    sandbox = Sandbox()
    sandbox.init()
    config.workspace_dir = sandbox.path
    
    client = get_client(config)
    tools = ToolRegistry(config.workspace_dir, config.allow_shell_commands, config.shell_command_allowlist, offline_mode=config.offline_mode, sandbox_mode=True)
    
    planner = Planner(client, tools, profile_name=agent)
    agent_loop = AgentLoop(client, tools, profile_name=agent, sandbox_mode=True)
    
    try:
        console.print(f"[bold]Building in Sandbox:[/bold] {goal}")
        task = planner.plan_task(goal)
        
        console.print("\n[bold]Executing Build Plan...[/bold]")
        agent_loop.run_task(task)
    except Exception as e:
        console.print(f"[red]Sandbox build failed: {e}[/red]")
        sys.exit(1)

def main():
    try:
        cli()
    except Exception as e:
        console.print(Panel(f"[bold red]Critical Error:[/bold red] {e}", title="System Crash", border_style="red"))
        console.print("[dim]Use --debug to see full traceback.[/dim]")
        # In a real scenario, we might want to log this to a file
        sys.exit(1)

if __name__ == "__main__":
    main()

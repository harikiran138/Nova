#!/usr/bin/env python3
"""Nova Agent CLI - Main entry point."""

import sys
import time
from pathlib import Path
import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.markdown import Markdown
from rich.table import Table

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent_core import Config, OllamaClient, AgentLoop
from src.agent_core.tools import ToolRegistry

console = Console()

def get_client(config: Config):
    """Get the appropriate model client based on config."""
    return OllamaClient(config.ollama_base_url, config.ollama_model)

def print_welcome(config: Config, client):
    """Print welcome message with configuration info."""
    import random
    from src.agent_core.tools import ToolRegistry
    
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
    
    console.print(Panel.fit(
        "[bold blue]✨ Nova — Autonomous Local Agent[/bold blue]\n"
        "[dim]No cloud. No tracking. Fully private.[/dim]\n\n"
        "System Status:\n"
        "  • [bold green]Identity:[/bold green] Nova v3.0 (Enhanced)\n"
        f"  • [bold green]Mode:[/bold green] {config.safety_level.upper()}\n"
        f"  • [bold green]Tools:[/bold green] {tool_count} enabled\n"
        f"  • [bold green]Workspace:[/bold green] {config.workspace_dir}\n\n"
        "[yellow]Tip:[/yellow] Type 'help' to see available commands or 'dashboard' for metrics.\n\n"
        "[dim]Nova Privacy Policy: All actions executed locally unless explicitly allowed.[/dim]",
        border_style="blue"
    ))


def select_model(client, config: Config) -> str:
    """Interactive model selection."""

    # Ollama Logic
    console.print("[dim]Fetching available models...[/dim]")
    models = client.get_available_models()
    
    if not models:
        console.print("[red]No models found. Please pull a model using 'ollama pull <model>'[/red]")
        return client.model
    
    table = Table(title="Available Models")
    table.add_column("#", style="cyan", justify="right")
    table.add_column("Model Name", style="green")
    
    for idx, model in enumerate(models, 1):
        table.add_row(str(idx), model)
    
    console.print(table)
    
    choices = [str(i) for i in range(1, len(models) + 1)]
    try:
        selection = IntPrompt.ask("Select a model", choices=choices)
        selected_model = models[selection - 1]
        console.print(f"[green]Selected model: {selected_model}[/green]")
        return selected_model
    except (ValueError, IndexError):
        console.print("[red]Invalid selection[/red]")
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
                spinner = console.status("[bold cyan]Nova is thinking...[/bold cyan]", spinner="dots12")
                spinner.start()
        elif event == "thinking_end":
            if spinner:
                spinner.stop()
                spinner = None
        elif event == "tool_start":
            if spinner: spinner.stop()
            tool_name, tool_args = args
            console.print(f"[dim]🔧 Executing: {tool_name}[/dim]")
            if spinner: spinner.start()
        elif event == "tool_end":
            if spinner: spinner.stop()
            tool_name, result = args
            if result["success"]:
                console.print(Panel(str(result.get("result", "")), title=f"✓ {tool_name}", border_style="green", expand=False))
            else:
                console.print(Panel(str(result.get("error", "")), title=f"✗ {tool_name}", border_style="red", expand=False))
            if spinner: spinner.start()

    agent = AgentLoop(client, tools, profile_name=profile_name, sandbox_mode=sandbox_mode, status_callback=status_handler)
    
    while True:
        try:
            user_input = console.input("\n[bold green]You>[/bold green] ").strip()
            if not user_input:
                continue
                
            if user_input.startswith("/"):
                action = handle_slash_command(user_input, agent, client, config)
                if action == "exit":
                    break
                elif action == "reload":
                    # Re-initialize client and agent with new config
                    client = get_client(config)
                    agent = AgentLoop(client, tools, profile_name=profile_name, sandbox_mode=sandbox_mode, status_callback=status_handler)
                    print_welcome(config, client)
                continue
            
            if user_input.lower() in ['exit', 'quit']:
                console.print("[yellow]Goodbye![/yellow]")
                break
            
            console.print()  # Empty line for spacing
            response = agent.process_input(user_input)
            
            # Stop spinner if stuck (safety)
            if spinner: spinner.stop()
            
            if response:
                from src.agent_core.utils import simulate_typing
                console.print("[bold green]Nova:[/bold green]")
                simulate_typing(response)
            else:
                console.print("[red]No response from agent.[/red]")
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


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
        response = agent.process_input(command)
        
        if response:
            console.print("\n[bold green]Nova:[/bold green]")
            console.print(Panel(Markdown(response), border_style="green", padding=(1, 2)))
        else:
            console.print("[red]Failed to get response.[/red]")
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error during execution: {e}[/red]")
        sys.exit(1)


from src.agent_core.planner import Planner
from src.agent_core.sandbox import Sandbox

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
    console.print(Panel(f"""
[bold]Nova Status[/bold]
Model Provider: [cyan]Ollama[/cyan]
Model: [cyan]{config.ollama_model}[/cyan]
Workspace: [yellow]{config.workspace_dir}[/yellow]
Sandbox Mode: [magenta]{'Active' if args.sandbox else 'Inactive'}[/magenta]
Agent Profile: [green]{args.agent or 'general'}[/green]
""", title="System Status", border_style="blue"))

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

    agent_loop.process_input(goal)

@cli.command()
def history():
    """Show session history."""
    config = Config.from_env()
    from src.agent_core.memory import MemoryManager
    memory = MemoryManager(config.workspace_dir / ".nova" / "memory")
    sessions = memory.list_sessions()
    
    if not sessions:
        console.print("No history found.")
        return
        
    table = Table(title="Nova Session History")
    table.add_column("ID", style="cyan")
    table.add_column("Time", style="dim")
    table.add_column("Last Action", style="white")
    
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
    
    # 2. Capabilities Report
    console.print("\n[bold]2. Comprehensive Capabilities Report[/bold]")
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
    from src.agent_core.sandbox import Sandbox
    from src.agent_core.planner import Planner
    
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

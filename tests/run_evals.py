import click
import sys
import importlib
from pathlib import Path
from rich.console import Console

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

console = Console()

@click.group()
def cli():
    """Nova Advanced AI Evaluation Runner."""
    pass

@cli.command()
@click.option('--suite', default='all', type=click.Choice(['reasoning', 'tools', 'memory', 'vision', 'safety', 'chaos', 'adversarial', 'longrun', 'degradation', 'security_level4', 'self_repair', 'all'], case_sensitive=False), help='Which test suite to run')
def run(suite):
    """Run specified evaluation suites."""
    console.print(f"[bold green]🤖 Starting Nova Eval Runner: Suite={suite.upper()}[/bold green]")
    
    suites_to_run = []
    
    if suite == 'all' or suite == 'reasoning':
        try:
            from tests.evals.reasoning.test_reasoning import ReasoningSuite
            suites_to_run.append(ReasoningSuite())
        except ImportError as e:
            console.print(f"[yellow]⚠ Could not load Reasoning Suite: {e}[/yellow]")

    if suite == 'all' or suite == 'tools':
        try:
            from tests.evals.tools.test_tools import ToolUseSuite
            suites_to_run.append(ToolUseSuite())
        except ImportError as e:
            console.print(f"[yellow]⚠ Could not load Tool Use Suite: {e}[/yellow]")

    if suite == 'all' or suite == 'memory':
        try:
            from tests.evals.memory.test_memory import MemorySuite
            suites_to_run.append(MemorySuite())
        except ImportError as e:
            console.print(f"[yellow]⚠ Could not load Memory Suite: {e}[/yellow]")

    if suite == 'all' or suite == 'vision':
        try:
            from tests.evals.vision.test_vision import VisionSuite
            suites_to_run.append(VisionSuite())
        except ImportError as e:
            console.print(f"[yellow]⚠ Could not load Vision Suite: {e}[/yellow]")

    if suite == 'all' or suite == 'safety':
        try:
            from tests.evals.safety.test_safety import SafetySuite
            suites_to_run.append(SafetySuite())
        except ImportError as e:
            console.print(f"[yellow]⚠ Could not load Safety Suite: {e}[/yellow]")

    if suite == 'all' or suite == 'chaos':
        try:
            from tests.evals.chaos.test_chaos import ChaosSuite
            suites_to_run.append(ChaosSuite())
        except ImportError as e:
            console.print(f"[yellow]⚠ Could not load Chaos Suite: {e}[/yellow]")

    if suite == 'all' or suite == 'adversarial':
        try:
            from tests.evals.adversarial.test_adversarial import AdversarialSuite
            suites_to_run.append(AdversarialSuite())
        except ImportError as e:
            console.print(f"[yellow]⚠ Could not load Adversarial Suite: {e}[/yellow]")

    if suite == 'all' or suite == 'longrun':
        try:
            from tests.evals.longrun.test_longrun import LongRunSuite
            suites_to_run.append(LongRunSuite())
        except ImportError as e:
            console.print(f"[yellow]⚠ Could not load LongRun Suite: {e}[/yellow]")

    if suite == 'all' or suite == 'degradation':
        try:
            from tests.evals.degradation.test_degradation import DegradationSuite
            suites_to_run.append(DegradationSuite())
        except ImportError as e:
            console.print(f"[yellow]⚠ Could not load Degradation Suite: {e}[/yellow]")
    if suite == 'all' or suite == 'security_level4':
        try:
            from tests.evals.safety.test_security_level4 import SecurityLevel4Suite
            suites_to_run.append(SecurityLevel4Suite())
        except ImportError as e:
            console.print(f"[yellow]⚠ Could not load Security Level 4 Suite: {e}[/yellow]")

    if suite == 'all' or suite == 'self_repair':
        try:
            from tests.evals.self_repair.test_self_repair import SelfRepairSuite
            suites_to_run.append(SelfRepairSuite())
        except ImportError as e:
            console.print(f"[yellow]⚠ Could not load Self Repair Suite: {e}[/yellow]")
    
    total_score = 0
    count = 0
    
    for s in suites_to_run:
        s.run()
        score = s.print_report()
        total_score += score
        count += 1
        
    if count > 0:
        avg_score = total_score / count
        console.print(f"[bold blue]🏆 Overall Average Score: {avg_score:.1f}%[/bold blue]")
    else:
        console.print("[yellow]No suites ran.[/yellow]")

if __name__ == "__main__":
    cli()

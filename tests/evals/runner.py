import json
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()

class EvalCase:
    """Represents a single test case in an evaluation suite."""
    def __init__(self, case_id: str, input_data: Any, expected: Any, category: str = "general"):
        self.case_id = case_id
        self.input_data = input_data
        self.expected = expected
        self.category = category

class EvalResult:
    """Represents the result of a single evaluation case."""
    def __init__(self, case_id: str, success: bool, output: Any, latency_ms: float, error: Optional[str] = None):
        self.case_id = case_id
        self.success = success
        self.output = output
        self.latency_ms = latency_ms
        self.error = error

class BaseEvalSuite(ABC):
    """Abstract base class for all evaluation suites."""
    
    def __init__(self, name: str):
        self.name = name
        self.results: List[EvalResult] = []

    @abstractmethod
    def load_cases(self) -> List[EvalCase]:
        """Load test cases from Hugging Face datasets or local files."""
        pass

    @abstractmethod
    def run_case(self, case: EvalCase) -> EvalResult:
        """Execute a single test case against the Nova agent."""
        pass

    def run(self):
        """Run all loaded cases and store results."""
        cases = self.load_cases()
        console.print(f"[bold blue]🚀 Running Suite: {self.name} ({len(cases)} cases)[/bold blue]")
        
        for case in cases:
            console.print(f"  Running {case.case_id}...", end="")
            try:
                result = self.run_case(case)
                self.results.append(result)
                if result.success:
                    console.print(f" [green]PASSED[/green] ({result.latency_ms:.1f}ms)")
                else:
                    console.print(f" [red]FAILED[/red] ({result.latency_ms:.1f}ms)")
                    if result.error:
                        console.print(f"    [red]Error:[/red] {result.error}")
            except Exception as e:
                console.print(f" [red]CRASHED[/red]: {e}")
                self.results.append(EvalResult(case.case_id, False, None, 0, str(e)))

    def print_report(self):
        """Print a summary table of results."""
        table = Table(title=f"Evaluation Report: {self.name}")
        table.add_column("ID", style="cyan")
        table.add_column("Success", style="magenta")
        table.add_column("Latency (ms)", justify="right")
        table.add_column("Output/Error")

        passed = 0
        for res in self.results:
            status = "[green]PASS[/green]" if res.success else "[red]FAIL[/red]"
            if res.success:
                passed += 1
            
            output_str = str(res.output)[:50] + "..." if res.output else str(res.error)
            table.add_row(res.case_id, status, f"{res.latency_ms:.1f}", output_str)

        console.print(table)
        success_rate = (passed / len(self.results)) * 100 if self.results else 0
        console.print(f"[bold]Success Rate: {success_rate:.1f}%[/bold]\n")
        return success_rate


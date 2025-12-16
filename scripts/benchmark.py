#!/usr/bin/env python3
"""
Nova Agent Benchmarking Suite.
Evaluates local Ollama models on performance and capability.
"""

import sys
import time
import json
import re
from pathlib import Path
from typing import List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent_core import Config, OllamaClient, ToolRegistry, AgentLoop

console = Console()

class BenchmarkSuite:
    def __init__(self):
        self.config = Config.from_env()
        # Initialize with default model, will override per test
        self.client = OllamaClient(self.config.ollama_base_url, self.config.ollama_model)
        self.tools = ToolRegistry(
            self.config.workspace_dir, 
            self.config.allow_shell_commands,
            self.config.shell_command_allowlist
        )
        
        self.test_cases = [
            {
                "name": "Chat (Simple)",
                "prompt": "Hello, who are you? Reply in one sentence.",
                "type": "chat",
                "expected_pattern": r"Nova|AI|assistant"
            },
            {
                "name": "Tool (File Write)",
                "prompt": "Create a file named 'bench_test.txt' with content 'BENCHMARK_PASS'.",
                "type": "tool",
                "expected_tool": "file.write",
                "verification_file": "bench_test.txt",
                "verification_content": "BENCHMARK_PASS"
            },
            {
                "name": "Tool (Shell)",
                "prompt": "List the files in the current directory using ls.",
                "type": "tool",
                "expected_tool": "shell.run"
            },
            {
                "name": "Reasoning (Math+File)",
                "prompt": "Calculate 12 * 8, then create a file named 'result.txt' with the answer.",
                "type": "reasoning",
                "expected_tool": "file.write",
                "verification_file": "result.txt",
                "verification_content": "96"
            }
        ]

    def get_models(self) -> List[str]:
        """Get list of available models."""
        models = self.client.get_available_models()
        # Filter for likely chat models
        return [m for m in models if "embed" not in m]

    def run_test(self, model: str, test: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test case on a model."""
        # Update client model
        self.client.model = model
        agent = AgentLoop(self.client, self.tools)
        
        start_time = time.time()
        try:
            # Run agent loop (limit to 3 iterations)
            response = agent.process_input(test["prompt"], max_iterations=3)
            duration = time.time() - start_time
            
            result = {
                "success": False,
                "duration": duration,
                "error": None,
                "output": response
            }

            if not response:
                result["error"] = "No response"
                return result

            # Verification
            if test["type"] == "chat":
                if re.search(test["expected_pattern"], response, re.IGNORECASE):
                    result["success"] = True
                else:
                    result["error"] = "Response didn't match pattern"

            elif test["type"] in ["tool", "reasoning"]:
                # Check history for tool calls
                tool_called = False
                for msg in agent.conversation_history:
                    if msg["role"] == "assistant" and '"tool":' in msg["content"]:
                        if test.get("expected_tool") in msg["content"]:
                            tool_called = True
                
                if not tool_called:
                    result["error"] = "Expected tool not called"
                else:
                    # Verify side effects if needed
                    if "verification_file" in test:
                        fpath = self.config.workspace_dir / test["verification_file"]
                        if fpath.exists():
                            content = fpath.read_text().strip()
                            if test["verification_content"] in content:
                                result["success"] = True
                            else:
                                result["error"] = f"File content mismatch. Got: {content}"
                        else:
                            result["error"] = "Verification file not created"
                    else:
                        result["success"] = True

            return result

        except Exception as e:
            return {
                "success": False,
                "duration": time.time() - start_time,
                "error": str(e),
                "output": ""
            }

    def run_suite(self):
        """Run full benchmark suite."""
        models = self.get_models()
        if not models:
            console.print("[red]No models found![/red]")
            return

        console.print(f"[bold cyan]🚀 Starting Nova Benchmark on {len(models)} models...[/bold cyan]")
        
        results = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        ) as progress:
            
            for model in models:
                model_task = progress.add_task(f"Testing {model}...", total=len(self.test_cases))
                model_results = []
                
                for test in self.test_cases:
                    progress.update(model_task, description=f"Testing {model}: {test['name']}")
                    res = self.run_test(model, test)
                    model_results.append({
                        "test": test["name"],
                        **res
                    })
                    progress.advance(model_task)
                
                results[model] = model_results

        self.print_report(results)
        self.save_report(results)

    def print_report(self, results: Dict[str, List[Dict[str, Any]]]):
        """Print results table."""
        table = Table(title="Nova Agent Model Benchmark")
        table.add_column("Model", style="cyan")
        table.add_column("Success Rate", justify="center")
        table.add_column("Avg Latency", justify="right")
        table.add_column("Chat", justify="center")
        table.add_column("Tools", justify="center")
        table.add_column("Reasoning", justify="center")

        for model, tests in results.items():
            success_count = sum(1 for t in tests if t["success"])
            total_time = sum(t["duration"] for t in tests)
            avg_time = total_time / len(tests)
            
            # Category results
            chat_res = next(t for t in tests if t["test"] == "Chat (Simple)")
            tool_res = next(t for t in tests if t["test"] == "Tool (File Write)")
            reason_res = next(t for t in tests if t["test"] == "Reasoning (Math+File)")
            
            def fmt_res(r):
                return "[green]✓[/green]" if r["success"] else "[red]✗[/red]"

            table.add_row(
                model,
                f"{success_count}/{len(tests)}",
                f"{avg_time:.2f}s",
                fmt_res(chat_res),
                fmt_res(tool_res),
                fmt_res(reason_res)
            )

        console.print(table)

    def save_report(self, results: Dict[str, List[Dict[str, Any]]]):
        """Save detailed markdown report."""
        report = "# Nova Agent Model Benchmark Report\n\n"
        report += f"**Date**: {time.strftime('%Y-%m-%d %H:%M')}\n\n"
        
        report += "## Summary Table\n\n"
        report += "| Model | Success Rate | Avg Latency | Chat | Tool Use | Reasoning |\n"
        report += "|-------|--------------|-------------|------|----------|-----------|\n"
        
        for model, tests in results.items():
            success_count = sum(1 for t in tests if t["success"])
            avg_time = sum(t["duration"] for t in tests) / len(tests)
            
            chat_res = "✅" if next(t for t in tests if t["test"] == "Chat (Simple)")["success"] else "❌"
            tool_res = "✅" if next(t for t in tests if t["test"] == "Tool (File Write)")["success"] else "❌"
            reason_res = "✅" if next(t for t in tests if t["test"] == "Reasoning (Math+File)")["success"] else "❌"
            
            report += f"| {model} | {success_count}/{len(tests)} | {avg_time:.2f}s | {chat_res} | {tool_res} | {reason_res} |\n"
        
        report += "\n## Detailed Results\n\n"
        for model, tests in results.items():
            report += f"### {model}\n\n"
            for t in tests:
                icon = "✅" if t["success"] else "❌"
                report += f"- **{t['test']}**: {icon} ({t['duration']:.2f}s)\n"
                if not t["success"]:
                    report += f"  - Error: {t['error']}\n"
            report += "\n"
            
        Path("benchmark_report.md").write_text(report)
        console.print("\n[green]Detailed report saved to benchmark_report.md[/green]")

if __name__ == "__main__":
    suite = BenchmarkSuite()
    suite.run_suite()

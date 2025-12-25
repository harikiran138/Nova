#!/usr/bin/env python3
"""
Nova Evals Runner - Run OpenAI Evals against Nova and generate clean report.

Usage:
    python3 evals/run_nova_evals.py [--light|--full]
    
    --light: Run quick reasoning tests only
    --full: Run comprehensive benchmark suite
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add Nova to path
sys.path.append(str(Path(__file__).parent.parent))


def run_simple_evals() -> Dict[str, Any]:
    """
    Run simple local evaluations without full OpenAI Evals framework.
    
    Returns:
        Dict with evaluation results
    """
    from evals.nova_completion_fn import NovaCompletionFn
    
    print("=" * 60)
    print("Nova Evaluation Suite (Lightweight)")
    print("=" * 60)
    
    # Initialize Nova
    print("\n[1/4] Initializing Nova...")
    try:
        completion_fn = NovaCompletionFn()
        print("✓ Nova initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize Nova: {e}")
        return {"error": str(e)}
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "model": completion_fn.model,
        "tests": []
    }
    
    # Test 1: Basic Reasoning
    print("\n[2/4] Testing Basic Reasoning...")
    reasoning_tests = [
        {
            "name": "arithmetic",
            "prompt": "What is 15 + 27?",
            "expected_keywords": ["42"]
        },
        {
            "name": "logic",
            "prompt": "If all roses are flowers and some flowers fade quickly, can we conclude that some roses fade quickly?",
            "expected_keywords": ["yes", "true", "correct"]
        },
        {
            "name": "sequence",
            "prompt": "What number comes next: 2, 4, 8, 16, ?",
            "expected_keywords": ["32"]
        }
    ]
    
    reasoning_score = 0
    for test in reasoning_tests:
        try:
            response = completion_fn(test["prompt"])
            # Simple keyword matching
            passed = any(kw.lower() in response.lower() for kw in test["expected_keywords"])
            reasoning_score += 1 if passed else 0
            
            results["tests"].append({
                "category": "reasoning",
                "name": test["name"],
                "passed": passed,
                "response": response[:100]  # Truncate for report
            })
            
            status = "✓" if passed else "✗"
            print(f"  {status} {test['name']}: {test['prompt'][:40]}...")
            
        except Exception as e:
            print(f"  ✗ {test['name']}: Error - {e}")
            results["tests"].append({
                "category": "reasoning",
                "name": test["name"],
                "passed": False,
                "error": str(e)
            })
    
    print(f"\n  Score: {reasoning_score}/{len(reasoning_tests)}")
    
    # Test 2: Instruction Following
    print("\n[3/4] Testing Instruction Following...")
    instruction_tests = [
        {
            "name": "format_json",
            "prompt": "Respond with a JSON object containing your name and version. Only output valid JSON, nothing else.",
            "validator": lambda r: r.strip().startswith("{") and r.strip().endswith("}")
        },
        {
            "name": "brevity",
            "prompt": "Answer in exactly 3 words: What is the capital of France?",
            "validator": lambda r: len(r.split()) <= 5  # Some tolerance
        }
    ]
    
    instruction_score = 0
    for test in instruction_tests:
        try:
            response = completion_fn(test["prompt"])
            passed = test["validator"](response)
            instruction_score += 1 if passed else 0
            
            results["tests"].append({
                "category": "instruction_following",
                "name": test["name"],
                "passed": passed,
                "response": response[:100]
            })
            
            status = "✓" if passed else "✗"
            print(f"  {status} {test['name']}")
            
        except Exception as e:
            print(f"  ✗ {test['name']}: Error - {e}")
            results["tests"].append({
                "category": "instruction_following",
                "name": test["name"],
                "passed": False,
                "error": str(e)
            })
    
    print(f"\n  Score: {instruction_score}/{len(instruction_tests)}")
    
    # Test 3: Tool Usage (if tools available)
    print("\n[4/4] Testing Nova-Specific Capabilities...")
    nova_tests = [
        {
            "name": "self_awareness",
            "prompt": "What is your name and what can you do?",
            "expected_keywords": ["nova", "agent", "autonomous"]
        }
    ]
    
    nova_score = 0
    for test in nova_tests:
        try:
            response = completion_fn(test["prompt"])
            passed = any(kw.lower() in response.lower() for kw in test["expected_keywords"])
            nova_score += 1 if passed else 0
            
            results["tests"].append({
                "category": "nova_specific",
                "name": test["name"],
                "passed": passed,
                "response": response[:100]
            })
            
            status = "✓" if passed else "✗"
            print(f"  {status} {test['name']}")
            
        except Exception as e:
            print(f"  ✗ {test['name']}: Error - {e}")
            results["tests"].append({
                "category": "nova_specific",
                "name": test["name"],
                "passed": False,
                "error": str(e)
            })
    
    print(f"\n  Score: {nova_score}/{len(nova_tests)}")
    
    # Calculate overall score
    total_tests = len(reasoning_tests) + len(instruction_tests) + len(nova_tests)
    total_passed = reasoning_score + instruction_score + nova_score
    
    results["summary"] = {
        "total_tests": total_tests,
        "passed": total_passed,
        "failed": total_tests - total_passed,
        "pass_rate": f"{(total_passed/total_tests)*100:.1f}%"
    }
    
    print("\n" + "=" * 60)
    print(f"Overall Score: {total_passed}/{total_tests} ({results['summary']['pass_rate']})")
    print("=" * 60)
    
    return results


def generate_report(results: Dict[str, Any], output_path: str = "reports/evals_report.md"):
    """Generate a clean markdown report from eval results."""
    
    Path(output_path).parent.mkdir(exist_ok=True)
    
    report = f"""# Nova Evaluation Report

**Generated**: {results.get('timestamp', 'Unknown')}  
**Model**: {results.get('model', 'Unknown')}

## Summary

- **Total Tests**: {results['summary']['total_tests']}
- **Passed**: {results['summary']['passed']}
- **Failed**: {results['summary']['failed']}
- **Pass Rate**: {results['summary']['pass_rate']}

## Test Results by Category

"""
    
    # Group by category
    categories = {}
    for test in results['tests']:
        category = test.get('category', 'unknown')
        if category not in categories:
            categories[category] = []
        categories[category].append(test)
    
    for category, tests in categories.items():
        report += f"### {category.replace('_', ' ').title()}\n\n"
        
        for test in tests:
            status = "✅" if test.get('passed') else "❌"
            name = test.get('name', 'unknown')
            report += f"- {status} **{name}**\n"
            
            if not test.get('passed') and 'error' in test:
                report += f"  - Error: `{test['error']}`\n"
        
        report += "\n"
    
    report += """## Recommendations

Based on the evaluation results:

"""
    
    if results['summary']['passed'] == results['summary']['total_tests']:
        report += "✅ All tests passed! Nova is performing excellently.\n"
    elif results['summary']['passed'] / results['summary']['total_tests'] >= 0.8:
        report += "⚠️ Most tests passed, but there's room for improvement in failed areas.\n"
    else:
        report += "❌ Significant failures detected. Review failed tests and improve corresponding capabilities.\n"
    
    # Write report
    
    # Write report
    Path(output_path).write_text(report)
    print(f"\n✓ Report saved to: {output_path}")
    
    return output_path


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "--light"
    
    if mode == "--full":
        print("Full evaluation suite not yet implemented.")
        print("Running lightweight evals instead...\n")
    
    # Run evals
    results = run_simple_evals()
    
    if "error" not in results:
        # Generate report
        report_path = generate_report(results)
        print(f"\n✅ Evaluation complete! See report: {report_path}")
    else:
        print(f"\n❌ Evaluation failed: {results['error']}")
        sys.exit(1)

"""
Custom Nova Evals - Testing Nova-specific capabilities.

These evals test Nova's unique features:
- Tool usage accuracy
- Multi-step reasoning
- File operations
- Web research capabilities
"""

import sys
from pathlib import Path
sysPath.append(str(Path(__file__).parent.parent))

from evals.elsuite.basic.match import Match
from evals.registry import Registry


# Register Nova completion function
def register_nova():
    """Register Nova as a completion function in evals registry."""
    from evals.nova_completion_fn import NovaCompletionFn
    
    registry = Registry()
    # Note: This is typically done via YAML, but we can do it programmatically
    print("Nova completion function ready for evals")


# Sample eval: Tool usage test
TOOL_USAGE_SAMPLES = [
    {
        "input": "What is 2 + 2?",
        "ideal": "4"
    },
    {
        "input": "Search for information about quantum computing",
        "ideal": ["quantum", "computing", "physics"]  # Should contain these keywords
    },
    {
        "input": "Create a file called test.txt with content 'Hello World'",
        "ideal": ["test.txt", "created", "Hello World"]
    }
]


# Sample eval: Reasoning test
REASONING_SAMPLES = [
    {
        "input": "If John is taller than Mary, and Mary is taller than Sue, who is the shortest?",
        "ideal": "Sue"
    },
    {
        "input": "A farmer has 17 sheep. All but 9 die. How many are left?",
        "ideal": "9"
    },
    {
        "input": "What comes next in the sequence: 2, 4, 8, 16, ...?",
        "ideal": "32"
    }
]

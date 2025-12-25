"""
Task-Specific Reasoning Router for AgentBench optimization.

Routes tasks to appropriate reasoning modes based on task type.
"""

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass


class ReasoningMode(Enum):
    """Reasoning modes for different task types."""
    STRICT_FINAL_ANSWER = "strict_final_answer"  # Arithmetic, sequences
    KEYWORD_ENFORCED = "keyword_enforced"  # Logic, constraints
    PROCEDURAL_STEP = "procedural_step"  # Problem solving, puzzles
    CONVERSATIONAL = "conversational"  # Multi-turn dialogue
    BENCHMARK_STRICT = "benchmark_strict"  # General benchmark mode


@dataclass
class TaskPolicy:
    """Policy configuration for a specific task type."""
    mode: ReasoningMode
    max_iterations: int = 10
    require_final_answer: bool = False
    required_keywords: Optional[list] = None
    required_verbs: Optional[list] = None
    required_numbers: Optional[list] = None
    format_validator: Optional[callable] = None
    allow_tools: bool = True
    tool_allowlist: Optional[list] = None


class ReasoningRouter:
    """
    Routes tasks to appropriate reasoning modes and policies.
    
    Optimizes agent behavior for different benchmark task types.
    """
    
    # Default policies for common task types
    POLICIES = {
        "arithmetic": TaskPolicy(
            mode=ReasoningMode.STRICT_FINAL_ANSWER,
            max_iterations=5,
            require_final_answer=True,
            allow_tools=False  # Simple math doesn't need tools
        ),
        "sequence": TaskPolicy(
            mode=ReasoningMode.STRICT_FINAL_ANSWER,
            max_iterations=5,
            require_final_answer=True,
            allow_tools=False
        ),
        "logic": TaskPolicy(
            mode=ReasoningMode.KEYWORD_ENFORCED,
            max_iterations=5,
            required_keywords=["no", "cannot", "some", "not all", "yes", "must"],
            allow_tools=False
        ),
        "problem_solving": TaskPolicy(
            mode=ReasoningMode.PROCEDURAL_STEP,
            max_iterations=10,
            required_verbs=["fill", "pour", "empty", "transfer"],
            allow_tools=False
        ),
        "conversation": TaskPolicy(
            mode=ReasoningMode.CONVERSATIONAL,
            max_iterations=3,
            allow_tools=True
        ),
        "format": TaskPolicy(
            mode=ReasoningMode.BENCHMARK_STRICT,
            max_iterations=3,
            allow_tools=False
        ),
        "constraint": TaskPolicy(
            mode=ReasoningMode.BENCHMARK_STRICT,
            max_iterations=3,
            allow_tools=False
        )
    }
    
    def __init__(self):
        self.current_policy = None
    
    def route(self, task_type: str, task_data: Dict[str, Any] = None) -> TaskPolicy:
        """
        Route task to appropriate policy.
        
        Args:
            task_type: Type of task (arithmetic, logic, etc.)
            task_data: Additional task metadata
            
        Returns:
            TaskPolicy for the task
        """
        # Get base policy
        policy = self.POLICIES.get(task_type.lower())
        
        if not policy:
            # Default to benchmark strict mode
            policy = TaskPolicy(
                mode=ReasoningMode.BENCHMARK_STRICT,
                max_iterations=5,
                allow_tools=False
            )
        
        # Customize based on task data
        if task_data:
            if "expected_answer" in task_data:
                policy.require_final_answer = True
            if "expected_keywords" in task_data:
                policy.required_keywords = task_data["expected_keywords"]
            if "required_verbs" in task_data:
                policy.required_verbs = task_data["required_verbs"]
            if "required_numbers" in task_data:
                policy.required_numbers = task_data["required_numbers"]
        
        self.current_policy = policy
        return policy
    
    def get_system_prompt(self, policy: TaskPolicy) -> str:
        """Get system prompt for the policy mode."""
        base_prompt = "You are a precise AI assistant optimized for benchmark tasks."
        
        if policy.mode == ReasoningMode.STRICT_FINAL_ANSWER:
            return f"""{base_prompt}

CRITICAL RULES:
1. Show your reasoning step by step
2. End with EXACTLY this format: FINAL_ANSWER: <your_answer>
3. Do not add any text after the final answer
4. The final answer must be a single number or value"""
        
        elif policy.mode == ReasoningMode.KEYWORD_ENFORCED:
            keywords = ", ".join(policy.required_keywords) if policy.required_keywords else "appropriate logical terms"
            return f"""{base_prompt}

CRITICAL RULES:
1. Your answer MUST include explicit logical markers
2. Required keywords to use: {keywords}
3. If stating a limitation, use: "cannot", "not all", "some"
4. If stating a conclusion, use: "yes", "no", "must"
5. Be explicit and literal in your language"""
        
        elif policy.mode == ReasoningMode.PROCEDURAL_STEP:
            return f"""{base_prompt}

CRITICAL RULES:
1. Break down the solution into numbered steps
2. Each step must describe a physical action
3. Use action verbs: fill, pour, empty, transfer
4. Include all relevant numbers and quantities
5. Format: "Step X: [Action verb] [details with numbers]" """
        
        elif policy.mode == ReasoningMode.CONVERSATIONAL:
            return f"""{base_prompt}

CRITICAL RULES:
1. Maintain context from previous turns
2. Acknowledge information from earlier in the conversation
3. Build on previous responses
4. Be concise but contextually aware"""
        
        else:  # BENCHMARK_STRICT
            return f"""{base_prompt}

BENCHMARK MODE - CRITICAL RULES:
1. Follow output format EXACTLY as specified
2. Do not add explanations unless requested
3. Do not be conversational
4. Include ALL required elements
5. Be literal and precise"""
    
    def should_use_tools(self, policy: TaskPolicy) -> bool:
        """Check if tools should be used for this policy."""
        return policy.allow_tools
    
    def get_tool_allowlist(self, policy: TaskPolicy) -> Optional[list]:
        """Get allowed tools for this policy."""
        return policy.tool_allowlist

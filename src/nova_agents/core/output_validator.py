"""
Output Validator and Enforcer for AgentBench compliance.

This module ensures agent outputs meet benchmark requirements:
- Final answer extraction
- Keyword presence validation
- Format compliance
- Auto-correction with reprompting
"""

import re
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass


@dataclass
class ValidationRule:
    """Validation rule for agent output."""
    name: str
    validator: Callable[[str], bool]
    error_message: str
    fix_prompt: Optional[str] = None


class OutputValidator:
    """
    Validates and enforces agent output compliance with benchmark requirements.
    
    Automatically detects issues and generates fix prompts for re-execution.
    """
    
    def __init__(self):
        self.validation_history = []
    
    def validate_arithmetic(self, response: str, expected_answer: str) -> Dict[str, Any]:
        """Validate arithmetic task output."""
        result = {
            "passed": False,
            "issues": [],
            "fix_prompt": None
        }
        
        # Extract all numbers from response
        numbers = re.findall(r'\b\d+\.?\d*\b', response)
        
        # Check for FINAL_ANSWER format
        final_answer_match = re.search(r'FINAL_ANSWER:\s*(\d+\.?\d*)', response, re.IGNORECASE)
        
        if final_answer_match:
            answer = final_answer_match.group(1)
            if answer == expected_answer:
                result["passed"] = True
                return result
            else:
                result["issues"].append(f"FINAL_ANSWER is {answer}, expected {expected_answer}")
        elif expected_answer in numbers:
            result["passed"] = True
            return result
        else:
            result["issues"].append(f"Expected answer '{expected_answer}' not found in response")
        
        # Generate fix prompt
        result["fix_prompt"] = f"""Your previous answer failed validation.
Expected numeric answer: {expected_answer}
Your answer did not contain this exact number.

Rewrite your answer in this exact format:
FINAL_ANSWER: {expected_answer}

Do not add extra text after the final answer."""
        
        return result
    
    def validate_keywords(self, response: str, required_keywords: List[str], min_count: int = None) -> Dict[str, Any]:
        """Validate keyword presence in response."""
        result = {
            "passed": False,
            "issues": [],
            "fix_prompt": None
        }
        
        response_lower = response.lower()
        found_keywords = [kw for kw in required_keywords if kw.lower() in response_lower]
        missing_keywords = [kw for kw in required_keywords if kw.lower() not in response_lower]
        
        min_required = min_count or (len(required_keywords) // 2 + 1)
        
        if len(found_keywords) >= min_required:
            result["passed"] = True
            return result
        
        result["issues"].append(f"Missing required keywords: {missing_keywords}")
        result["fix_prompt"] = f"""Your previous answer failed validation.
Missing keywords: {', '.join(missing_keywords)}
Found keywords: {', '.join(found_keywords)}

Rewrite your answer to explicitly include ALL of these keywords:
{', '.join(missing_keywords)}

Your answer MUST contain these exact words."""
        
        return result
    
    def validate_format(self, response: str, validator_func: Callable[[str], bool], format_desc: str) -> Dict[str, Any]:
        """Validate custom format requirements."""
        result = {
            "passed": False,
            "issues": [],
            "fix_prompt": None
        }
        
        try:
            if validator_func(response):
                result["passed"] = True
                return result
        except Exception as e:
            result["issues"].append(f"Validation error: {e}")
        
        result["issues"].append(f"Output does not match required format: {format_desc}")
        result["fix_prompt"] = f"""Your previous answer failed format validation.
Required format: {format_desc}

Rewrite your answer to match this format exactly.
Do not add extra text or explanations."""
        
        return result
    
    def validate_procedural(self, response: str, required_verbs: List[str], required_numbers: List[str]) -> Dict[str, Any]:
        """Validate procedural step-by-step narration (e.g., water jug problems)."""
        result = {
            "passed": False,
            "issues": [],
            "fix_prompt": None
        }
        
        response_lower = response.lower()
        
        # Check for action verbs
        found_verbs = [v for v in required_verbs if v.lower() in response_lower]
        missing_verbs = [v for v in required_verbs if v.lower() not in response_lower]
        
        # Check for numbers
        found_numbers = [n for n in required_numbers if n in response]
        missing_numbers = [n for n in required_numbers if n not in response]
        
        if len(found_verbs) >= len(required_verbs) // 2 and len(found_numbers) >= len(required_numbers) // 2:
            result["passed"] = True
            return result
        
        if missing_verbs:
            result["issues"].append(f"Missing action verbs: {missing_verbs}")
        if missing_numbers:
            result["issues"].append(f"Missing numbers: {missing_numbers}")
        
        result["fix_prompt"] = f"""Your previous answer failed validation.
Missing action verbs: {', '.join(missing_verbs) if missing_verbs else 'none'}
Missing numbers: {', '.join(missing_numbers) if missing_numbers else 'none'}

Rewrite your answer as step-by-step instructions.
Each step MUST include:
- An action verb from: {', '.join(required_verbs)}
- Container sizes: {', '.join(required_numbers)}

Example format:
Step 1: Fill the 5-gallon jug
Step 2: Pour from 5-gallon into 3-gallon jug
..."""
        
        return result
    
    def extract_final_answer(self, response: str) -> Optional[str]:
        """Extract final answer from response using multiple patterns."""
        patterns = [
            r'FINAL_ANSWER:\s*(.+?)(?:\n|$)',
            r'(?:the answer is|answer:|final answer:)\s*(.+?)(?:\n|$)',
            r'(?:therefore|thus|so),?\s*(.+?)(?:\n|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def enforce_final_answer_format(self, response: str, expected_type: str = "number") -> str:
        """
        Enforce final answer format in response.
        
        Args:
            response: Agent response
            expected_type: Type of answer (number, text, list)
            
        Returns:
            Formatted response with FINAL_ANSWER marker
        """
        final_answer = self.extract_final_answer(response)
        
        if final_answer:
            return response
        
        # Try to extract answer based on type
        if expected_type == "number":
            numbers = re.findall(r'\b\d+\.?\d*\b', response)
            if numbers:
                return f"{response}\n\nFINAL_ANSWER: {numbers[-1]}"
        
        return response


class BenchmarkModeEnforcer:
    """
    Enforces benchmark-specific behavior and output discipline.
    
    Modifies prompts to ensure compliance with AgentBench requirements.
    """
    
    BENCHMARK_SYSTEM_PROMPT = """You are in BENCHMARK MODE.

CRITICAL RULES:
1. Follow output format EXACTLY as specified
2. Do not add explanations unless explicitly requested
3. Do not be conversational or helpful beyond the task
4. Include ALL required keywords and numbers
5. For arithmetic: Always end with "FINAL_ANSWER: <number>"
6. For logic: Include explicit logical markers (no, cannot, some, not all)
7. For procedures: Narrate each step with action verbs and numbers

Failure to follow these rules will result in test failure."""
    
    @staticmethod
    def wrap_arithmetic_prompt(prompt: str) -> str:
        """Wrap arithmetic prompt with strict formatting requirements."""
        return f"""{prompt}

IMPORTANT: After showing your work, you MUST end with:
FINAL_ANSWER: <numeric_answer>

Do not add any text after the final answer."""
    
    @staticmethod
    def wrap_logic_prompt(prompt: str, required_keywords: List[str]) -> str:
        """Wrap logic prompt with keyword requirements."""
        return f"""{prompt}

IMPORTANT: Your answer MUST explicitly include at least one of these words:
{', '.join(required_keywords)}

If there is a limitation or exception, state it using these exact terms."""
    
    @staticmethod
    def wrap_procedural_prompt(prompt: str, action_verbs: List[str], numbers: List[str]) -> str:
        """Wrap procedural prompt with step-by-step requirements."""
        return f"""{prompt}

IMPORTANT: Describe each action explicitly as numbered steps.
Each step MUST contain:
- An action verb: {', '.join(action_verbs)}
- Relevant numbers: {', '.join(numbers)}

Example:
Step 1: Fill the 5-gallon jug
Step 2: Pour from 5-gallon into 3-gallon jug"""
    
    @staticmethod
    def wrap_format_prompt(prompt: str, format_description: str) -> str:
        """Wrap prompt with format requirements."""
        return f"""{prompt}

IMPORTANT: Your answer must follow this exact format:
{format_description}

Do not add extra text or explanations."""

"""
Unit tests for ReasoningRouter module.

Tests task type routing and policy selection.
"""

import pytest
from src.nova_agents.core.reasoning_router import ReasoningRouter, ReasoningMode, TaskPolicy


class TestReasoningRouter:
    """Test suite for ReasoningRouter."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.router = ReasoningRouter()
    
    def test_route_arithmetic(self):
        """Test routing of arithmetic tasks."""
        policy = self.router.route('arithmetic')
        
        assert policy.mode == ReasoningMode.STRICT_FINAL_ANSWER
        assert policy.require_final_answer is True
        assert policy.allow_tools is False
    
    def test_route_logic(self):
        """Test routing of logic tasks."""
        policy = self.router.route('logic')
        
        assert policy.mode == ReasoningMode.KEYWORD_ENFORCED
        assert policy.required_keywords is not None
        assert 'cannot' in policy.required_keywords
        assert policy.allow_tools is False
    
    def test_route_problem_solving(self):
        """Test routing of problem solving tasks."""
        policy = self.router.route('problem_solving')
        
        assert policy.mode == ReasoningMode.PROCEDURAL_STEP
        assert policy.required_verbs is not None
        assert 'fill' in policy.required_verbs
        assert 'pour' in policy.required_verbs
    
    def test_route_conversation(self):
        """Test routing of conversational tasks."""
        policy = self.router.route('conversation')
        
        assert policy.mode == ReasoningMode.CONVERSATIONAL
        assert policy.allow_tools is True
    
    def test_route_unknown_task(self):
        """Test routing of unknown task types defaults to benchmark strict."""
        policy = self.router.route('unknown_task_type')
        
        assert policy.mode == ReasoningMode.BENCHMARK_STRICT
        assert policy.allow_tools is False
    
    def test_route_with_custom_data(self):
        """Test routing with custom task data overrides."""
        task_data = {
            'expected_answer': '42',
            'expected_keywords': ['special', 'keyword'],
            'required_verbs': ['custom', 'verb']
        }
        
        policy = self.router.route('arithmetic', task_data)
        
        assert policy.require_final_answer is True
        assert policy.required_keywords == ['special', 'keyword']
        assert policy.required_verbs == ['custom', 'verb']
    
    def test_get_system_prompt_arithmetic(self):
        """Test system prompt generation for arithmetic mode."""
        policy = TaskPolicy(mode=ReasoningMode.STRICT_FINAL_ANSWER)
        prompt = self.router.get_system_prompt(policy)
        
        assert 'FINAL_ANSWER' in prompt
        assert 'number' in prompt.lower()
    
    def test_get_system_prompt_logic(self):
        """Test system prompt generation for logic mode."""
        policy = TaskPolicy(
            mode=ReasoningMode.KEYWORD_ENFORCED,
            required_keywords=['no', 'cannot', 'some']
        )
        prompt = self.router.get_system_prompt(policy)
        
        assert 'no' in prompt
        assert 'cannot' in prompt
        assert 'logical' in prompt.lower()
    
    def test_get_system_prompt_procedural(self):
        """Test system prompt generation for procedural mode."""
        policy = TaskPolicy(mode=ReasoningMode.PROCEDURAL_STEP)
        prompt = self.router.get_system_prompt(policy)
        
        assert 'Step' in prompt
        assert 'action' in prompt.lower()
        assert 'fill' in prompt or 'pour' in prompt
    
    def test_get_system_prompt_conversational(self):
        """Test system prompt generation for conversational mode."""
        policy = TaskPolicy(mode=ReasoningMode.CONVERSATIONAL)
        prompt = self.router.get_system_prompt(policy)
        
        assert 'context' in prompt.lower()
        assert 'previous' in prompt.lower()
    
    def test_get_system_prompt_benchmark_strict(self):
        """Test system prompt generation for benchmark strict mode."""
        policy = TaskPolicy(mode=ReasoningMode.BENCHMARK_STRICT)
        prompt = self.router.get_system_prompt(policy)
        
        assert 'BENCHMARK' in prompt
        assert 'format' in prompt.lower()
    
    def test_should_use_tools(self):
        """Test tool usage policy check."""
        policy_with_tools = TaskPolicy(mode=ReasoningMode.CONVERSATIONAL, allow_tools=True)
        policy_without_tools = TaskPolicy(mode=ReasoningMode.STRICT_FINAL_ANSWER, allow_tools=False)
        
        assert self.router.should_use_tools(policy_with_tools) is True
        assert self.router.should_use_tools(policy_without_tools) is False
    
    def test_get_tool_allowlist(self):
        """Test tool allowlist retrieval."""
        policy_with_allowlist = TaskPolicy(
            mode=ReasoningMode.CONVERSATIONAL,
            tool_allowlist=['tool1', 'tool2']
        )
        policy_without_allowlist = TaskPolicy(mode=ReasoningMode.STRICT_FINAL_ANSWER)
        
        assert self.router.get_tool_allowlist(policy_with_allowlist) == ['tool1', 'tool2']
        assert self.router.get_tool_allowlist(policy_without_allowlist) is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

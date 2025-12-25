"""
Unit tests for OutputValidator module.

Tests validation of arithmetic, logic, and procedural task outputs.
"""

import pytest
from src.nova_agents.core.output_validator import OutputValidator, BenchmarkModeEnforcer


class TestOutputValidator:
    """Test suite for OutputValidator."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.validator = OutputValidator()
    
    def test_arithmetic_with_final_answer(self):
        """Test arithmetic validation with proper FINAL_ANSWER format."""
        response = "Let me calculate: 37 + 37 = 74\n\nFINAL_ANSWER: 74"
        result = self.validator.validate_arithmetic(response, "74")
        
        assert result['passed'] is True
        assert len(result['issues']) == 0
        assert result['fix_prompt'] is None
    
    def test_arithmetic_without_final_answer(self):
        """Test arithmetic validation failure when FINAL_ANSWER is missing."""
        response = "The answer is 74"
        result = self.validator.validate_arithmetic(response, "75")
        
        assert result['passed'] is False
        assert len(result['issues']) > 0
        assert result['fix_prompt'] is not None
    
    def test_arithmetic_wrong_answer(self):
        """Test arithmetic validation with incorrect answer."""
        response = "FINAL_ANSWER: 73"
        result = self.validator.validate_arithmetic(response, "74")
        
        assert result['passed'] is False
        assert "FINAL_ANSWER is 73, expected 74" in result['issues'][0]
    
    def test_keywords_all_present(self):
        """Test keyword validation when all required keywords are present."""
        response = "No, not all birds can fly. Some species cannot fly."
        required = ["no", "cannot", "some", "not all"]
        result = self.validator.validate_keywords(response, required, min_count=2)
        
        assert result['passed'] is True
    
    def test_keywords_missing(self):
        """Test keyword validation when required keywords are missing."""
        response = "Birds have wings and feathers."
        required = ["no", "cannot", "some", "not all"]
        result = self.validator.validate_keywords(response, required, min_count=1)
        
        assert result['passed'] is False
        assert result['fix_prompt'] is not None
        assert "no" in result['fix_prompt']
    
    def test_procedural_with_verbs_and_numbers(self):
        """Test procedural validation with action verbs and numbers."""
        response = """Step 1: Fill the 5-gallon jug
Step 2: Pour from 5-gallon into 3-gallon jug
Step 3: Empty the 3-gallon jug
Step 4: Fill gives us 4 gallons"""
        
        required_verbs = ["fill", "pour", "empty"]
        required_numbers = ["3", "5", "4"]
        result = self.validator.validate_procedural(response, required_verbs, required_numbers)
        
        assert result['passed'] is True
    
    def test_procedural_missing_verbs(self):
        """Test procedural validation when action verbs are missing."""
        response = "Use the 5-gallon and 3-gallon jugs to get 4 gallons."
        
        required_verbs = ["fill", "pour", "empty"]
        required_numbers = ["3", "5", "4"]
        result = self.validator.validate_procedural(response, required_verbs, required_numbers)
        
        assert result['passed'] is False
        assert result['fix_prompt'] is not None
    
    def test_extract_final_answer_standard(self):
        """Test extraction of final answer from standard format."""
        response = "Calculation complete.\n\nFINAL_ANSWER: 42"
        answer = self.validator.extract_final_answer(response)
        
        assert answer == "42"
    
    def test_extract_final_answer_alternate(self):
        """Test extraction of final answer from alternate formats."""
        response = "Therefore, the answer is: 42"
        answer = self.validator.extract_final_answer(response)
        
        assert answer == "42"
    
    def test_extract_final_answer_none(self):
        """Test extraction when no final answer marker is present."""
        response = "This is just some text without an answer."
        answer = self.validator.extract_final_answer(response)
        
        assert answer is None


class TestBenchmarkModeEnforcer:
    """Test suite for BenchmarkModeEnforcer."""
    
    def test_wrap_arithmetic_prompt(self):
        """Test arithmetic prompt wrapping."""
        original = "What is 5 + 3?"
        wrapped = BenchmarkModeEnforcer.wrap_arithmetic_prompt(original)
        
        assert "FINAL_ANSWER" in wrapped
        assert original in wrapped
        assert "numeric_answer" in wrapped
    
    def test_wrap_logic_prompt(self):
        """Test logic prompt wrapping with keywords."""
        original = "Can all animals swim?"
        keywords = ["no", "cannot", "some"]
        wrapped = BenchmarkModeEnforcer.wrap_logic_prompt(original, keywords)
        
        assert original in wrapped
        assert "no" in wrapped
        assert "cannot" in wrapped
        assert "some" in wrapped
    
    def test_wrap_procedural_prompt(self):
        """Test procedural prompt wrapping."""
        original = "How do you measure 4 gallons?"
        verbs = ["fill", "pour", "empty"]
        numbers = ["3", "5"]
        wrapped = BenchmarkModeEnforcer.wrap_procedural_prompt(original, verbs, numbers)
        
        assert original in wrapped
        assert "Step 1" in wrapped
        assert "fill" in wrapped.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

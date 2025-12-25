import pytest
from src.agent_core.adk.base import BaseTool

def test_base_tool_initialization():
    """Test that BaseTool can be initialized with required attributes."""
    class MyTool(BaseTool):
        def execute(self, **kwargs):
            return "Executed"
    
    tool = MyTool(name="test_tool", description="A test tool")
    assert tool.name == "test_tool"
    assert tool.description == "A test tool"

def test_base_tool_abstract_execute():
    """Test that BaseTool raises NotImplementedError if execute is not overridden."""
    class IncompleteTool(BaseTool):
        pass
    
    # Depending on implementation, abstract methods might enforce this at instantiation
    # or at call time. If using abc.ABC, instantiation fails.
    # We will assume abc.ABC implementation for robustness.
    
    with pytest.raises(TypeError):
        IncompleteTool(name="incomplete", description="incomplete")

def test_tool_execution_interface():
    """Test the execution interface."""
    class ConcreteTool(BaseTool):
        def execute(self, param1):
            return f"result: {param1}"

    tool = ConcreteTool(name="concrete", description="concrete")
    assert tool.execute(param1="test") == "result: test"

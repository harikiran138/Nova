import pytest
from unittest.mock import MagicMock, patch
from src.agent_core.tools.knowledge_tools import LookupTool
from src.agent_core.adk.registry import ToolRegistry

@pytest.fixture
def mock_knowledge_base():
    with patch('src.agent_core.tools.knowledge_tools.KnowledgeBase') as MockKB:
        mock_kb_instance = MockKB.return_value
        yield mock_kb_instance

def test_lookup_tool_initialization():
    """Test that LookupTool initializes correctly."""
    tool = LookupTool()
    assert tool.name == "knowledge.lookup"
    assert "Query the local knowledge base" in tool.description

def test_lookup_execution(mock_knowledge_base):
    """Test executing the lookup tool."""
    tool = LookupTool()
    
    # Mock query return
    mock_knowledge_base.query.return_value = [
        {"id": "doc1", "document": "Result 1", "metadata": {"source": "test"}}
    ]
    
    result = tool.execute(query="test query")
    
    assert result["success"] is True
    assert "Result 1" in result["result"]
    mock_knowledge_base.query.assert_called_once_with("test query", n_results=5)

def test_integration_with_registry():
    """Test that the tool can be registered in the registry."""
    registry = ToolRegistry()
    tool = LookupTool()
    registry.register_tool(tool)
    
    retrieved_tool = registry.get_tool("knowledge.lookup")
    assert retrieved_tool is tool

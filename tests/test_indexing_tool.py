import os
import pytest
from unittest.mock import MagicMock, patch
from src.agent_core.tools.knowledge_tools import IndexingTool

@pytest.fixture
def mock_knowledge_base():
    with patch('src.agent_core.tools.knowledge_tools.KnowledgeBase') as MockKB:
        mock_kb_instance = MockKB.return_value
        yield mock_kb_instance

def test_indexing_tool_initialization():
    """Test that IndexingTool initializes correctly."""
    tool = IndexingTool()
    assert tool.name == "knowledge.index"
    assert "Recursively indexes" in tool.description

def test_indexing_execution(mock_knowledge_base, tmp_path):
    """Test indexing a directory."""
    # Create some dummy files
    (tmp_path / "file1.txt").write_text("Content 1")
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir/file2.md").write_text("Content 2")
    
    tool = IndexingTool()
    
    # Mock os.walk or let it run on tmp_path (easier to let it run)
    result = tool.execute(directory=str(tmp_path))
    
    assert result["success"] is True
    assert "Indexed 2 files" in result["result"]
    
    # Check if add_document was called
    assert mock_knowledge_base.add_document.call_count == 2
    
    # Verify calls
    calls = mock_knowledge_base.add_document.call_args_list
    
    # Extract contents from kwargs
    contents = []
    for call in calls:
        # call is a tuple (args, kwargs)
        # content is passed as keyword argument 'content'
        if 'content' in call[1]:
            contents.append(call[1]['content'])
    
    assert "Content 1" in contents
    assert "Content 2" in contents

def test_indexing_nonexistent_directory(mock_knowledge_base):
    """Test indexing a non-existent directory."""
    tool = IndexingTool()
    result = tool.execute(directory="/non/existent/path")
    
    assert result["success"] is False
    assert "does not exist" in result["error"]
    mock_knowledge_base.add_document.assert_not_called()
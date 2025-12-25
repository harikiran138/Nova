import pytest
from unittest.mock import MagicMock, patch
from src.agent_core.knowledge_base import KnowledgeBase

@pytest.fixture
def mock_chroma_client():
    with patch('chromadb.PersistentClient') as mock_client:
        yield mock_client

def test_knowledge_base_initialization(mock_chroma_client):
    """Test that KnowledgeBase initializes the ChromaDB client."""
    kb = KnowledgeBase(persist_directory="./test_db")
    assert kb.persist_directory == "./test_db"
    mock_chroma_client.assert_called_once_with(path="./test_db")

def test_add_document(mock_chroma_client):
    """Test adding a document to the knowledge base."""
    # Setup the mock client to return a mock instance
    mock_client_instance = mock_chroma_client.return_value
    mock_collection = MagicMock()
    mock_client_instance.get_or_create_collection.return_value = mock_collection
    
    kb = KnowledgeBase(persist_directory="./test_db")
    
    kb.add_document("doc1", "This is a test document.", {"source": "test"})
    
    mock_collection.add.assert_called_once()
    call_args = mock_collection.add.call_args[1]
    assert "ids" in call_args and call_args["ids"] == ["doc1"]
    assert "documents" in call_args and call_args["documents"] == ["This is a test document."]
    assert "metadatas" in call_args and call_args["metadatas"] == [{"source": "test"}]

def test_query_documents(mock_chroma_client):
    """Test querying documents."""
    # Setup the mock client to return a mock instance
    mock_client_instance = mock_chroma_client.return_value
    mock_collection = MagicMock()
    mock_client_instance.get_or_create_collection.return_value = mock_collection
    
    kb = KnowledgeBase(persist_directory="./test_db")
    
    mock_collection.query.return_value = {
        "ids": [["doc1"]],
        "documents": [["This is a test document."]],
        "metadatas": [[{"source": "test"}]]
    }
    
    results = kb.query("test query", n_results=1)
    
    mock_collection.query.assert_called_once()
    assert len(results) == 1
    assert results[0]["id"] == "doc1"
    assert results[0]["document"] == "This is a test document."
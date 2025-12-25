import chromadb
from typing import List, Dict, Any, Optional
import uuid

class KnowledgeBase:
    """
    Local Knowledge Base using ChromaDB for storing and retrieving documents.
    """
    def __init__(self, persist_directory: str = ".nova/chroma_db", collection_name: str = "nova_knowledge"):
        """
        Initialize the KnowledgeBase.

        Args:
            persist_directory: Path to store the ChromaDB data.
            collection_name: Name of the collection to use.
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_document(self, doc_id: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a document to the knowledge base.

        Args:
            doc_id: Unique identifier for the document.
            content: Text content of the document.
            metadata: Optional metadata dictionary.
        """
        if metadata is None:
            metadata = {}
        
        self.collection.add(
            ids=[doc_id],
            documents=[content],
            metadatas=[metadata]
        )

    def query(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Query the knowledge base for relevant documents.

        Args:
            query_text: The search query.
            n_results: Number of results to return.

        Returns:
            List of dictionaries containing 'id', 'document', and 'metadata'.
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )

        formatted_results = []
        if results['ids']:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "document": results['documents'][0][i] if results['documents'] else "",
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {}
                })
        
        return formatted_results

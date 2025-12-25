import os
from typing import Dict, Any
from src.nova_agents.adk.base import BaseTool
from src.nova_ai.knowledge_base import KnowledgeBase

class IndexingTool(BaseTool):
    """
    Tool to recursively index files in a directory into the local knowledge base.
    """
    def __init__(self):
        super().__init__(
            name="knowledge.index",
            description="Recursively indexes text files in a directory into the local knowledge base."
        )
        self.kb = KnowledgeBase()

    def execute(self, directory: str, **kwargs) -> Dict[str, Any]:
        """
        Execute the indexing process.

        Args:
            directory: The root directory to start indexing from.
            
        Returns:
            Dict containing success status and result message.
        """
        if not os.path.exists(directory):
            return {"success": False, "error": f"Directory '{directory}' does not exist."}

        count = 0
        try:
            for root, _, files in os.walk(directory):
                for file in files:
                    # Filter for common text files
                    if file.endswith(('.md', '.txt', '.py', '.json', '.yaml', '.yml', '.sh')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                
                            # Create a unique ID (e.g., file path)
                            doc_id = os.path.relpath(file_path, start=directory)
                            
                            self.kb.add_document(
                                doc_id=doc_id,
                                content=content,
                                metadata={"source": file_path, "filename": file}
                            )
                            count += 1
                        except Exception as e:
                            # Skip files that can't be read
                            continue
            
            return {"success": True, "result": f"Indexed {count} files from '{directory}'."}
            
        except Exception as e:
            return {"success": False, "error": f"Indexing failed: {str(e)}"}

class LookupTool(BaseTool):
    """
    Tool to query the local knowledge base.
    """
    def __init__(self):
        super().__init__(
            name="knowledge.lookup",
            description="Query the local knowledge base for relevant information. Use this to find code snippets, documentation, or facts stored locally."
        )
        self.kb = KnowledgeBase()

    def execute(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Execute the lookup.

        Args:
            query: The search query.
            
        Returns:
            Dict containing the search results.
        """
        try:
            results = self.kb.query(query, n_results=5)
            if not results:
                return {"success": True, "result": "No relevant information found."}
            
            formatted_output = "Found relevant information:\n\n"
            for i, res in enumerate(results):
                metadata = res.get('metadata', {})
                source = metadata.get('source', 'Unknown Source')
                formatted_output += f"--- Result {i+1} (Source: {source}) ---\n"
                formatted_output += f"{res.get('document')}\n\n"
            
            return {"success": True, "result": formatted_output}
        except Exception as e:
            return {"success": False, "error": f"Lookup failed: {str(e)}"}


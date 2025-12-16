import os
from pathlib import Path
from typing import List, Dict, Any

class RagEngine:
    """Retrieval-Augmented Generation Engine."""
    
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir
        self.collection = None
        self.client = None
        self._init_db()

    def _init_db(self):
        try:
            import chromadb
            from chromadb.config import Settings
            
            db_path = self.workspace_dir / ".nova" / "rag_db"
            db_path.mkdir(parents=True, exist_ok=True)
            
            self.client = chromadb.PersistentClient(path=str(db_path))
            self.collection = self.client.get_or_create_collection(name="nova_workspace")
        except ImportError:
            print("Warning: chromadb not installed. RAG disabled.")
        except Exception as e:
            print(f"Warning: RAG initialization failed: {e}")

    def index_workspace(self):
        """Index all text files in the workspace."""
        if not self.collection: return
        
        documents = []
        metadatas = []
        ids = []
        
        # Simple walk, skip hidden and binary
        for root, _, files in os.walk(self.workspace_dir):
            if ".git" in root or ".nova" in root: continue
            
            for file in files:
                if file.startswith("."): continue
                file_path = Path(root) / file
                
                try:
                    # Skip binary/large files
                    if file_path.stat().st_size > 100 * 1024: continue 
                    
                    content = file_path.read_text(errors='ignore')
                    if not content.strip(): continue
                    
                    documents.append(content)
                    metadatas.append({"source": str(file_path.relative_to(self.workspace_dir))})
                    ids.append(str(file_path))
                except Exception:
                    continue
        
        if documents:
            try:
                self.collection.upsert(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                print(f"RAG: Indexed {len(documents)} files.")
            except Exception as e:
                print(f"RAG Index Error: {e}")

    def search(self, query: str, n_results: int = 3) -> List[str]:
        """Search for relevant context."""
        if not self.collection: return []
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            return results['documents'][0]
        except Exception as e:
            print(f"RAG Search Error: {e}")
            return []

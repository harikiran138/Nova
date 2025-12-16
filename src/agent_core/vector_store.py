import json
import math
from pathlib import Path
from typing import List, Dict, Any, Optional

class VectorStore:
    """Lightweight Vector Store using Ollama Embeddings and JSON storage."""
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load()

    def add(self, text: str, metadata: Dict[str, Any] = None):
        """Generate embedding and store text."""
        embedding = self._get_embedding(text)
        if embedding:
            entry = {
                "text": text,
                "embedding": embedding,
                "metadata": metadata or {}
            }
            self.data.append(entry)
            self._save()

    def search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Search for similar texts."""
        query_embedding = self._get_embedding(query)
        if not query_embedding:
            return []
            
        # Calculate cosine similarity
        results = []
        for entry in self.data:
            score = self._cosine_similarity(query_embedding, entry["embedding"])
            results.append({**entry, "score": score})
            
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding from Ollama."""
        try:
            import requests
            # Assuming Ollama is running on localhost:11434
            response = requests.post(
                "http://127.0.0.1:11434/api/embeddings",
                json={"model": "all-minilm", "prompt": text}, # Use a default embedding model if available, or fall back to main model
                timeout=5
            )
            if response.status_code == 200:
                return response.json().get("embedding")
            
            # Fallback: Try main model (might be slow but works)
            response = requests.post(
                "http://127.0.0.1:11434/api/embeddings",
                json={"model": "mannix/llama3.1-8b-abliterated", "prompt": text}, 
                timeout=5
            )
            if response.status_code == 200:
                return response.json().get("embedding")
                
        except Exception as e:
            pass
        return None

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm_v1 = math.sqrt(sum(a * a for a in v1))
        norm_v2 = math.sqrt(sum(b * b for b in v2))
        return dot_product / (norm_v1 * norm_v2) if norm_v1 > 0 and norm_v2 > 0 else 0.0

    def _load(self) -> List[Dict]:
        if self.storage_path.exists():
            try:
                return json.loads(self.storage_path.read_text())
            except:
                return []
        return []

    def _save(self):
        self.storage_path.write_text(json.dumps(self.data))

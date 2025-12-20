import json
import math
import os
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional

class VectorStore:
    """Lightweight Vector Store using Google AI Edge (MediaPipe) or Ollama."""
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load()
        
        # Google AI Edge (MediaPipe) Setup
        self.use_mediapipe = False
        self.embedder = None
        self.model_path = "universal_sentence_encoder.tflite"
        
        try:
            import mediapipe as mp
            from mediapipe.tasks import python
            from mediapipe.tasks.python import text
            
            # Auto-download model if missing
            if not os.path.exists(self.model_path):
                print("Downloading Google AI Edge Embedding Model...")
                url = "https://storage.googleapis.com/mediapipe-tasks/text_embedder/universal_sentence_encoder.tflite"
                try:
                    r = requests.get(url, timeout=60)
                    if r.status_code == 200:
                        with open(self.model_path, "wb") as f:
                            f.write(r.content)
                        print("Model downloaded successfully.")
                except Exception as e:
                    print(f"Failed to download embedding model: {e}")

            if os.path.exists(self.model_path):
                base_options = python.BaseOptions(model_asset_path=self.model_path)
                options = text.TextEmbedderOptions(base_options=base_options)
                self.embedder = text.TextEmbedder.create_from_options(options)
                self.use_mediapipe = True
                print("Google AI Edge (MediaPipe) Embedder initialized.")
        except ImportError:
            print("MediaPipe not installed. Falling back to Ollama.")
        except Exception as e:
            print(f"Error initializing MediaPipe Embedder: {e}")

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
        """Get embedding from MediaPipe (Fast) or Ollama (Slow)."""
        if self.use_mediapipe and self.embedder:
            try:
                # print("DEBUG: Generating embedding via Google AI Edge (MediaPipe)...") # Optional debug
                embedding_result = self.embedder.embed(text)
                return embedding_result.embeddings[0].embedding.tolist()
            except Exception as e:
                print(f"Error: MediaPipe Embedding failed: {e}")
                print("Falling back to Ollama...")
                # Fallthrough to Ollama

        # Fallback: Ollama
        try:
            # Assuming Ollama is running on localhost:11434
            response = requests.post(
                "http://127.0.0.1:11434/api/embeddings",
                json={"model": "all-minilm", "prompt": text}, 
                timeout=5
            )
            if response.status_code == 200:
                return response.json().get("embedding")
            
            # Fallback: Try main model 
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
        if not v1 or not v2: return 0.0
        # Ensure vectors are same length (handle different models)
        if len(v1) != len(v2): return 0.0
        
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

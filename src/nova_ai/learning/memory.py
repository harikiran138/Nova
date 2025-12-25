from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..vector_store import VectorStore

class KnowledgeStore:
    """
    Manages long-term memory for the agent using VectorStore.
    Stores 'Facts' (declarative knowledge) and 'Skills' (procedural knowledge).
    """
    def __init__(self, workspace_dir: Path):
        self.store = VectorStore(workspace_dir / ".nova" / "memory" / "knowledge_store.json")

    def add_fact(self, topic: str, content: str, source: str, confidence: float = 1.0):
        """Store a learned fact about a topic."""
        metadata = {
            "type": "fact",
            "topic": topic,
            "source": source,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }
        # We embed the content combined with topic for better retrieval
        text_to_embed = f"{topic}: {content}"
        self.store.add(text_to_embed, metadata)

    def add_skill(self, problem: str, solution_steps: str, verified: bool = False):
        """Store a learned skill (how-to)."""
        metadata = {
            "type": "skill",
            "problem": problem,
            "verified": verified,
            "timestamp": datetime.now().isoformat()
        }
        text_to_embed = f"Problem: {problem}\nSolution:\n{solution_steps}"
        self.store.add(text_to_embed, metadata)

    def search(self, query: str, limit: int = 3, min_confidence: float = 0.0) -> List[Dict[str, Any]]:
        """Retrieve relevant knowledge."""
        results = self.store.search(query, limit=limit)
        
        filtered = []
        for r in results:
            meta = r.get("metadata", {})
            # If it's a fact, check confidence
            if meta.get("type") == "fact" and meta.get("confidence", 0) < min_confidence:
                continue
            filtered.append(r)
            
        return filtered

    def get_all_facts(self) -> List[str]:
        """Return a string representation of recent facts."""
        # This is a simple retrieval, in a real system we might query specifically
        return [f"{r['text']} (Source: {r['metadata'].get('source')})" for r in self.store.data if r['metadata'].get('type') == 'fact']

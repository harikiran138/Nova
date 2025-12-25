import json
import time
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict

@dataclass
class Session:
    id: str
    timestamp: float
    history: List[Dict[str, str]]
    metadata: Dict[str, Any]

class MemoryManager:
    """Manages persistence of agent sessions using MongoDB."""
    
    def __init__(self, memory_dir: Path):
        self.memory_dir = memory_dir # Kept for file-based fallback/secrets
        
        from src.nova_shared.config import Config
        config = Config.from_env()
        
        self.use_fallback = not config.use_mongodb
        
        if config.use_mongodb:
            try:
                from src.api.database import get_database
                from pymongo.errors import PyMongoError
                self.db = get_database()
                self.sessions = self.db.sessions
                self.facts = self.db.facts
                self.cache = self.db.cache
                self.general = self.db.general_memory
                
                # Ensure indexes
                self.sessions.create_index("id", unique=True)
                self.facts.create_index("fact", unique=True)
                self.episodes = self.db.episodes
                self.episodes.create_index("task")
                print("Connected to MongoDB for memory.")
            except Exception as e:
                print(f"Warning: MongoDB not available ({e}). Using file-based fallback.")
                self.use_fallback = True
        
        if self.use_fallback:
            # Ensure directories exist
            (self.memory_dir / "sessions").mkdir(parents=True, exist_ok=True)
            (self.memory_dir / "episodes").mkdir(parents=True, exist_ok=True)
        
    def save_session(self, session_id: str, history: List[Dict[str, str]], metadata: Dict[str, Any] = None):
        """Save a session to MongoDB or File."""
        session_data = {
            "id": session_id,
            "timestamp": time.time(),
            "history": history,
            "metadata": metadata or {}
        }
        
        if self.use_fallback:
            try:
                with open(self.memory_dir / "sessions" / f"{session_id}.json", "w") as f:
                    json.dump(session_data, f, indent=2)
            except Exception as e:
                print(f"Failed to save session to file: {e}")
        else:
            self.sessions.update_one(
                {"id": session_id},
                {"$set": session_data},
                upsert=True
            )
        
    def load_session(self, session_id: str) -> Optional[Session]:
        """Load a specific session from MongoDB or File."""
        data = None
        if self.use_fallback:
            try:
                p = self.memory_dir / "sessions" / f"{session_id}.json"
                if p.exists():
                    with open(p, "r") as f:
                        data = json.load(f)
            except Exception as e:
                print(f"Failed to load session from file: {e}")
        else:
            data = self.sessions.find_one({"id": session_id})
            
        if data:
            return Session(
                id=data["id"],
                timestamp=data["timestamp"],
                history=data["history"],
                metadata=data["metadata"]
            )
        return None
        
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all saved sessions (summary)."""
        if self.use_fallback:
            sessions = []
            try:
                for p in (self.memory_dir / "sessions").glob("*.json"):
                    with open(p, "r") as f:
                        data = json.load(f)
                        sessions.append(data)
                sessions.sort(key=lambda x: x["timestamp"], reverse=True)
                return [
                    {
                        "id": s["id"], 
                        "timestamp": s["timestamp"], 
                        "preview": s["history"][-1]["content"][:50] if s.get("history") else "Empty"
                    }
                    for s in sessions
                ]
            except Exception:
                return []
        else:
            cursor = self.sessions.find().sort("timestamp", -1)
            return [
                {
                    "id": s["id"], 
                    "timestamp": s["timestamp"], 
                    "preview": s["history"][-1]["content"][:50] if s.get("history") else "Empty"
                }
                for s in cursor
            ]

    # --- Caching System ---
    def get_cached_response(self, prompt: str) -> Optional[str]:
        """Retrieve cached response for a prompt."""
        key = str(hash(prompt))
        
        if self.use_fallback:
            try:
                cache_file = self.memory_dir / "cache.json"
                if cache_file.exists():
                    with open(cache_file, "r") as f:
                        cache = json.load(f)
                        return cache.get(key)
                return None
            except Exception:
                return None
            
        doc = self.cache.find_one({"key": key})
        return doc["response"] if doc else None

    def cache_response(self, prompt: str, response: str):
        """Cache a response."""
        key = str(hash(prompt))
        
        if self.use_fallback:
            try:
                cache_file = self.memory_dir / "cache.json"
                cache = {}
                if cache_file.exists():
                    with open(cache_file, "r") as f:
                        cache = json.load(f)
                
                cache[key] = response
                with open(cache_file, "w") as f:
                    json.dump(cache, f, indent=2)
            except Exception as e:
                print(f"Failed to cache response to file: {e}")
            return

        self.cache.update_one(
            {"key": key},
            {"$set": {"key": key, "prompt": prompt, "response": response}},
            upsert=True
        )

    # --- Adaptive Learning ---
    def add_fact(self, fact: str):
        """Learn a new fact and store in Vector DB."""
        if self.use_fallback:
            try:
                facts_file = self.memory_dir / "facts.json"
                facts = []
                if facts_file.exists():
                    with open(facts_file, "r") as f:
                        facts = json.load(f)
                
                # Check for duplicate
                if not any(item["fact"] == fact for item in facts):
                    facts.append({"fact": fact, "timestamp": time.time()})
                    with open(facts_file, "w") as f:
                        json.dump(facts, f, indent=2)
                    
                    # RAG Ingestion (Same for both)
                    try:
                        from src.api.rag import ingest_text
                        ingest_text(fact, source="learned_fact")
                    except Exception as e:
                        print(f"Failed to ingest learner fact: {e}")
            except Exception as e:
                 print(f"Failed to save fact to file: {e}")
        else:
            if not self.facts.find_one({"fact": fact}):
                self.facts.insert_one({"fact": fact, "timestamp": time.time()})
                # RAG Ingestion
                try:
                    from src.api.rag import ingest_text
                    ingest_text(fact, source="learned_fact")
                except Exception as e:
                    print(f"Failed to ingest learner fact: {e}")

    def get_facts(self) -> List[str]:
        """Get all learned facts."""
        if self.use_fallback:
            try:
                facts_file = self.memory_dir / "facts.json"
                if facts_file.exists():
                    with open(facts_file, "r") as f:
                        facts = json.load(f)
                    facts.sort(key=lambda x: x["timestamp"], reverse=True)
                    return [f["fact"] for f in facts]
                return []
            except Exception:
                return []
        else:
            cursor = self.facts.find().sort("timestamp", -1)
            return [f["fact"] for f in cursor]

    def semantic_search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Search long-term memory using Chroma vector search."""
        try:
            from src.api.rag import get_vector_store
            vector_store = get_vector_store()
            results = vector_store.similarity_search(query, k=limit)
            return [{"content": r.page_content, "metadata": r.metadata} for r in results]
        except Exception as e:
            print(f"Semantic search failed: {e}")
            return []

    # --- Episodic Memory (Task Success Patterns) ---
    def save_episode(self, episode: Dict[str, Any]):
        """Save a successful task execution episode."""
        episode["timestamp"] = time.time()
        if self.use_fallback:
            try:
                task = episode.get("task", "unknown")
                episodes_file = self.memory_dir / "episodes" / f"{task}.json"
                episodes = []
                if episodes_file.exists():
                    with open(episodes_file, "r") as f:
                        episodes = json.load(f)
                
                episodes.append(episode)
                with open(episodes_file, "w") as f:
                    json.dump(episodes, f, indent=2)
            except Exception as e:
                print(f"Failed to save episode to file: {e}")
        else:
            self.episodes.insert_one(episode)

    def get_episodes(self, task: str = None) -> List[Dict[str, Any]]:
        """Retrieve successful episodes, optionally filtered by task."""
        if self.use_fallback:
            try:
                if task:
                    p = self.memory_dir / "episodes" / f"{task}.json"
                    if p.exists():
                        with open(p, "r") as f:
                            return json.load(f)
                    return []
                else:
                    all_episodes = []
                    for p in (self.memory_dir / "episodes").glob("*.json"):
                        with open(p, "r") as f:
                            all_episodes.extend(json.load(f))
                    return all_episodes
            except Exception:
                return []
        else:
            query = {"task": task} if task else {}
            return list(self.episodes.find(query).sort("timestamp", -1))

    # --- General Memory ---
    # --- General Memory ---
    def remember(self, key: str, value: str):
        """Remember a specific key-value pair."""
        if self.use_fallback:
            # Simplified fallback for general key-value
            pass 
        else:
            self.general.update_one(
                {"key": key},
                {"$set": {"key": key, "value": value}},
                upsert=True
            )

    def recall(self, key: str) -> Optional[str]:
        """Recall a specific key-value pair."""
        if self.use_fallback:
             return None
        else:
            doc = self.general.find_one({"key": key})
            return doc["value"] if doc else None

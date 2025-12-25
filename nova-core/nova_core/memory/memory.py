import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from ..config import config

class MemorySystem:
    """SQLite-based memory system for conversation history and structured data."""
    
    def __init__(self, db_path: Path = None):
        self.db_path = db_path or config.database_path
        self._init_db()
        
    def _init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Conversations table
        c.execute('''CREATE TABLE IF NOT EXISTS conversations
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      session_id TEXT,
                      role TEXT,
                      content TEXT,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
                      
        # Key-Value store for preferences/state
        c.execute('''CREATE TABLE IF NOT EXISTS kv_store
                     (key TEXT PRIMARY KEY,
                      value TEXT,
                      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
                      
        conn.commit()
        conn.close()
        
    def add_message(self, session_id: str, role: str, content: str):
        """Add a message to history."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO conversations (session_id, role, content) VALUES (?, ?, ?)",
                  (session_id, role, content))
        conn.commit()
        conn.close()
        
    def get_history(self, session_id: str, limit: int = 50) -> List[Dict[str, str]]:
        """Get conversation history."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT role, content FROM conversations WHERE session_id = ? ORDER BY id ASC LIMIT ?",
                  (session_id, limit))
        rows = c.fetchall()
        conn.close()
        return [{"role": r["role"], "content": r["content"]} for r in rows]
        
    def set_value(self, key: str, value: Any):
        """Set a key-value pair."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        json_val = json.dumps(value)
        c.execute("INSERT OR REPLACE INTO kv_store (key, value) VALUES (?, ?)", (key, json_val))
        conn.commit()
        conn.close()
        
    def get_value(self, key: str) -> Any:
        """Get a value by key."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT value FROM kv_store WHERE key = ?", (key,))
        row = c.fetchone()
        conn.close()
        return json.loads(row[0]) if row else None

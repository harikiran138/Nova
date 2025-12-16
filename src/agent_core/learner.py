import time
import json
from pathlib import Path
from typing import List, Dict, Any

from src.agent_core.memory import MemoryManager
from src.agent_core.config import Config
from src.agent_core.model_client import OllamaClient
from src.api.rag import get_llm

class ContinuousLearner:
    """
    Background process that monitors agent sessions and extracts persistent facts/knowledge.
    """
    def __init__(self, memory_dir: Path):
        self.memory = MemoryManager(memory_dir)
        self.processed_file = memory_dir / "processed_sessions.json"
        self.processed_ids = self._load_processed()

    def _load_processed(self) -> set:
        if self.processed_file.exists():
            with open(self.processed_file, 'r') as f:
                return set(json.load(f))
        return set()

    def _save_processed(self):
        with open(self.processed_file, 'w') as f:
            json.dump(list(self.processed_ids), f)

    def extract_facts(self, session_id: str, history: List[Dict]) -> List[str]:
        """Use LLM to extract facts from a session."""
        # Only process sessions with substance
        if len(history) < 2: 
            return []
            
        # Construct prompt
        transcript = "\\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in history])
        prompt = f"""
        Analyze the following conversation and extract 1-3 key factual statements or useful learnings.
        Focus on user preferences, project details, or executed tasks.
        Format output as a bulleted list. If nothing worth learning, return 'No facts'.

        TRANSCRIPT:
        {transcript}
        """
        
        try:
           # Use configured LLM (via RAG module abstraction or direct client)
           # For simplicity here, we assume a direct call or use the one from config
           from langchain_core.messages import HumanMessage
           llm = get_llm()
           response = llm.invoke([HumanMessage(content=prompt)])
           content = response.content
           
           facts = []
           for line in content.split('\n'):
               line = line.strip()
               # Support standard bullets, numbered lists, and [1] style
               if line.startswith(('- ', '* ', '1. ', '[1]')):
                   # Clean up the marker
                   for marker in ['- ', '* ', '1. ', '[1] ']:
                       if line.startswith(marker):
                           fact = line[len(marker):].strip()
                           break
                   else:
                       fact = line # Should not happen given if check
                   
                   if len(fact) > 10:
                       facts.append(fact)
               # Also catch "Key factual statement:" lines typical of tinyllama
               elif "Key factual statement:" in line:
                   fact = line.split("Key factual statement:")[-1].strip()
                   if len(fact) > 10:
                       facts.append(fact)

           return facts
        except Exception as e:
            print(f"Extraction failed: {e}")
            return []

    def run_once(self):
        """Run one pass of learning."""
        sessions = self.memory.list_sessions() # Returns summaries
        # We need full objects, list_sessions only gives summaries. 
        # But we can iterate IDs.
        
        count = 0
        for s_summary in sessions:
            s_id = s_summary['id']
            if s_id in self.processed_ids:
                continue
                
            print(f"🧠 Learning from session {s_id}...")
            session = self.memory.load_session(s_id)
            if not session: continue
            
            facts = self.extract_facts(s_id, session.history)
            for fact in facts:
                print(f"  + Learned: {fact}")
                self.memory.add_fact(f"Learned from {s_id}: {fact}")
                
            self.processed_ids.add(s_id)
            count += 1
            
        if count > 0:
            self._save_processed()
            print(f"✅ Processed {count} new sessions.")
        else:
            print("💤 No new sessions to process.")

def main():
    config = Config.from_env()
    memory_dir = config.workspace_dir / ".nova" / "memory"
    learner = ContinuousLearner(memory_dir)
    learner.run_once()

if __name__ == "__main__":
    main()

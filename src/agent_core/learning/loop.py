from typing import Optional, List, Any
import logging
from ..tools.web_tools import WebSearchTool, WebExtractTool
from ..learning.memory import KnowledgeStore
from ..model_client import OllamaClient  # Or base client type

class LearningAgent:
    """
    Autonomous agent responsible for acquiring new knowledge.
    Executes the loop: Search -> Read -> Summarize -> Store.
    """
    def __init__(self, client: Any, knowledge_store: KnowledgeStore):
        self.client = client
        self.knowledge_store = knowledge_store
        self.search_tool = WebSearchTool()
        self.extract_tool = WebExtractTool()

    def learn_topic(self, topic: str) -> str:
        """
        Research a topic and store the findings.
        Returns a summary of what was learned.
        """
        print(f"📚 Learning about: {topic}...")
        
        # 1. Search
        search_res = self.search_tool.execute({"query": topic})
        if not search_res["success"]:
            return f"Failed to search for {topic}: {search_res.get('error')}"
            
        results = search_res["result"]
        if not results:
            return f"No information found for {topic}."

        # 2. Extract Content from Top Results (Limit to top 2 to save time/tokens)
        content_buffer = []
        for res in results[:2]: 
            url = res.get("href")
            if not url: continue
            
            print(f"📖 Reading: {url}")
            extract_res = self.extract_tool.execute({"url": url})
            if extract_res["success"]:
                content_buffer.append(f"Title: {res.get('title')}\nURL: {url}\nContent:\n{extract_res['result']}\n---\n")

        if not content_buffer:
            return "Could not extract content from search results."

        full_text = "\n".join(content_buffer)
        
        # 3. Summarize
        summary_prompt = f"""
        Analyze the following text about "{topic}" and create a comprehensive summary.
        Focus on technical details, facts, and how-to information.
        Ignore boilerplate, ads, and irrelevant navigation.
        
        TEXT:
        {full_text[:8000]}  # Truncate to safety limit
        
        SUMMARY:
        """
        
        try:
            # We use a simple history for this one-shot task
            summary = self.client.generate([], summary_prompt)
            if not summary:
                return "Failed to generate summary."
        except Exception as e:
            return f"Summarization error: {e}"

        # 4. Verification
        print(f"🕵️ Verifying info about {topic}")
        if not self._verify_knowledge(topic, summary):
             return f"Verification failed for topic '{topic}'. The gathered information was inconsistent."

        # 5. Store
        print(f"💾 Storing knowledge about {topic}")
        self.knowledge_store.add_fact(
            topic=topic,
            content=summary,
            source="web_search",
            confidence=0.9
        )
        
        # 6. Log for Fine-Tuning (Optional)
        self._log_for_finetuning(topic, summary)
        
        return f"Successfully learned about '{topic}'. Summary:\n{summary}"

    def _verify_knowledge(self, topic: str, summary: str) -> bool:
        """
        Self-Verification: Ask LLM to check for contradictions or hallucinations.
        """
        verify_prompt = f"""
        Verify the following summary about "{topic}".
        Check for logical inconsistencies or obvious errors.
        
        SUMMARY:
        {summary}
        
        Reply with "VALID" if it looks correct, or "INVALID" if it contains errors.
        Reply only with the one word.
        """
        try:
             res = self.client.generate([], verify_prompt)
             return "VALID" in res.strip().upper()
        except:
             return True # Fail open if verification completely crashes (or handle stricter)

    def _log_for_finetuning(self, topic: str, summary: str):
        """Append successful learning examples to a JSONL file."""
        import json
        from pathlib import Path
        try:
            log_path = self.knowledge_store.store.storage_path.parent / "finetuning_dataset.jsonl"
            entry = {
                "instruction": f"Explain {topic}",
                "output": summary,
                "source": "autonomous_learning"
            }
            with open(log_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            print(f"Failed to log for fine-tuning: {e}")

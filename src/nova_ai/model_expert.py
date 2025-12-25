from typing import List, Dict, Any
import os

class ModelExpert:
    """
    Ranks and suggests best local/cloud models for specific task domains
    using data from Hugging Face.
    """
    def __init__(self, hug_face_mcp=None):
        self.mcp = hug_face_mcp
        self.recommendations_cache = {}

    def suggest_model(self, task_description: str) -> Dict[str, Any]:
        """
        Suggests a model based on the task description and cached data.
        """
        import json
        from pathlib import Path
        
        cache_path = Path(__file__).parent / "model_cache.json"
        cache = []
        if cache_path.exists():
            try:
                cache = json.loads(cache_path.read_text())
            except:
                pass
        
        task_lower = task_description.lower()
        
        # Domain detection
        domain = "general"
        if any(kw in task_lower for kw in ["code", "python", "script", "refactor"]):
            domain = "coding"
        elif any(kw in task_lower for kw in ["vision", "image", "detect", "classify"]):
            domain = "vision"
        
        # Match from cache
        if domain == "coding" and cache:
            model = cache[0] # Simplistic: take top one
            return {"name": model["id"], "provider": "huggingface", "reason": model["description"]}
            
        if domain == "vision":
            return {"name": "google/vit-base-patch16-224", "provider": "huggingface", "reason": "Strong vision baseline."}
        
        return {"name": "gemini-1.5-flash", "provider": "google", "reason": "General purpose high-speed reasoning."}

    def rank_models(self, task: str, models: List[str]) -> List[str]:
        """Ranks a list of models for a specific task."""
        # Simple heuristic ranking for now
        return sorted(models, key=lambda x: ("llama" in x.lower() or "gemini" in x.lower()), reverse=True)

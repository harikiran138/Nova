from typing import Dict, Any, Optional
import base64
from pathlib import Path
from .base import BaseTool
from src.nova_ai.model_client import OllamaClient

class VisionTool(BaseTool):
    """
    Vision capabilities using local multi-modal models (Llava).
    """
    
    def __init__(self, model: str = "llava"):
        self.model = model
        # efficient client for vision, separate from main agent loop if needed
        # but we can reuse the standard Ollama client approach
        self.client = OllamaClient(base_url="http://localhost:11434", model=model)

    @property
    def name(self) -> str:
        return "vision.analyze"

    @property
    def description(self) -> str:
        return "vision.analyze(image_path, query) - Analyze an image and answer a question about it. Argument 'image_path' can be a local file path."

    def execute(self, **kwargs) -> Dict[str, Any]:
        image_path = kwargs.get("image_path")
        query = kwargs.get("query", "Describe this image.")
        
        if not image_path:
            return {"success": False, "error": "Missing image_path"}

        try:
            # 1. Validate Image
            path = Path(image_path)
            if not path.exists():
                return {"success": False, "error": f"Image file not found: {image_path}"}
            
            # 2. Encode Image
            with open(path, "rb") as image_file:
                image_bytes = image_file.read()
                # Ollama expects list of base64 strings (or bytes in some clients, but raw API takes base64)
                # The python library 'ollama' handles paths automatically in some versions, 
                # but our OllamaClient might calculate it manually.
                # Let's use the 'ollama' library directly if available for simplicity with vision,
                # OR adapt our OllamaClient.
                # For compatibility, let's try direct API call or use our client if it supports images.
                
            # Our OllamaClient implementation in src.nova_ai.model_client might not support images yet.
            # Let's do a direct request to be safe and robust.
            
            import requests
            import base64
            
            b64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            payload = {
                "model": self.model,
                "prompt": query,
                "images": [b64_image],
                "stream": False
            }
            
            response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=60)
            response.raise_for_status()
            result_json = response.json()
            
            analysis = result_json.get("response", "")
            
            return {
                "success": True, 
                "result": analysis,
                "metadata": {"model": self.model}
            }
            
        except Exception as e:
            return {"success": False, "error": f"Vision analysis failed: {str(e)}"}
"""Vision tools powered by Google MediaPipe."""

import os
from typing import Dict, Any, List
try:
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    HAS_MEDIAPIPE = True
except ImportError:
    HAS_MEDIAPIPE = False

class VisionTool:
    """Tool for analyzing images using local Edge AI (MediaPipe)."""
    
    description = "vision.analyze(image_path) - Analyze an image locally to identify objects and labels."

    def __init__(self):
        self.model_path = "models/mobilenet_v2_float.tflite" # Standard efficient model
        
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the vision analysis."""
        image_path = args.get("image_path")
        if not image_path:
            return {"success": False, "error": "Missing 'image_path' argument."}
            
        if not os.path.exists(image_path):
            return {"success": False, "error": f"Image file not found: {image_path}"}
            
        if not HAS_MEDIAPIPE:
            return {"success": False, "error": "MediaPipe library not installed."}

        try:
            return self.analyze_image(image_path)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Internal method to run MediaPipe inference."""
        # Create an ImageClassifier object.
        base_options = python.BaseOptions(model_asset_path=self.model_path)
        options = vision.ImageClassifierOptions(base_options=base_options, max_results=5)
        
        try:
            classifier = vision.ImageClassifier.create_from_options(options)
            
            # Load the input image.
            image = mp.Image.create_from_file(image_path)
            
            # Classify the input image.
            classification_result = classifier.classify(image)
            
            # Parse results
            labels = []
            if classification_result.classifications:
                for category in classification_result.classifications[0].categories:
                    labels.append({
                        "label": category.category_name,
                        "score": category.score
                    })
            
            return {
                "success": True, 
                "result": {
                    "labels": labels,
                    "top_match": labels[0]["label"] if labels else "unknown"
                }
            }
        except Exception as e:
            # Fallback for when model file is missing, etc.
            return {"success": False, "error": f"Inference failed: {e}"}
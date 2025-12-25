from typing import Dict, Any, List
import tempfile
import requests
import os
from .base import BaseTool

class VisionTool(BaseTool):
    def __init__(self):
        self.detector_model_path = "efficientdet_lite0.tflite"
        self.classifier_model_path = "efficientnet_lite0.tflite"
        self._download_models_if_needed()

    def _download_models_if_needed(self):
        # Base URLs for MediaPipe models
        base_url = "https://storage.googleapis.com/mediapipe-models/"
        
        # Object Detection Model
        if not os.path.exists(self.detector_model_path):
            url = "https://storage.googleapis.com/mediapipe-tasks/object_detector/efficientdet_lite0.tflite"
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    with open(self.detector_model_path, 'wb') as f:
                        f.write(response.content)
            except Exception as e:
                print(f"Warning: Failed to download detector model: {e}")

        # Image Classification Model
        if not os.path.exists(self.classifier_model_path):
            url = "https://storage.googleapis.com/mediapipe-tasks/image_classifier/efficientnet_lite0.tflite"
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    with open(self.classifier_model_path, 'wb') as f:
                        f.write(response.content)
            except Exception as e:
                print(f"Warning: Failed to download classifier model: {e}")

    @property
    def name(self) -> str:
        return "vision"

    @property
    def description(self) -> str:
        return "vision - Tools for seeing and understanding images (object detection, classification)."

    def detect_objects(self, image_path: str) -> List[Dict[str, Any]]:
        """Detect objects in an image."""
        try:
            import mediapipe as mp
            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision
        except ImportError:
            return [{"error": "mediapipe not installed. Run 'pip install mediapipe'"}]
        except Exception as e:
            return [{"error": f"Failed to load vision dependencies: {e}"}]

        if not os.path.exists(self.detector_model_path):
            return [{"error": "Detector model not found. Check internet connection."}]

        try:
            base_options = python.BaseOptions(model_asset_path=self.detector_model_path)
            options = vision.ObjectDetectorOptions(base_options=base_options, score_threshold=0.5)
            detector = vision.ObjectDetector.create_from_options(options)

            image = mp.Image.create_from_file(image_path)
            detection_result = detector.detect(image)
            
            results = []
            for detection in detection_result.detections:
                category = detection.categories[0]
                bbox = detection.bounding_box
                results.append({
                    "object": category.category_name,
                    "score": float(category.score),
                    "box": {
                        "x": bbox.origin_x,
                        "y": bbox.origin_y,
                        "width": bbox.width,
                        "height": bbox.height
                    }
                })
            return results
        except Exception as e:
            return [{"error": str(e)}]

    def classify_image(self, image_path: str) -> List[Dict[str, Any]]:
        """Classify what is in an image."""
        try:
            import mediapipe as mp
            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision
        except ImportError:
            return [{"error": "mediapipe not installed. Run 'pip install mediapipe'"}]
        except Exception as e:
            return [{"error": f"Failed to load vision dependencies: {e}"}]

        if not os.path.exists(self.classifier_model_path):
            return [{"error": "Classifier model not found."}]

        try:
            base_options = python.BaseOptions(model_asset_path=self.classifier_model_path)
            options = vision.ImageClassifierOptions(base_options=base_options, max_results=3)
            classifier = vision.ImageClassifier.create_from_options(options)

            image = mp.Image.create_from_file(image_path)
            classification_result = classifier.classify(image)
            
            # Reprocess results for cleaner output
            top_categories = classification_result.classifications[0].categories
            return [{"label": c.category_name, "score": float(c.score)} for c in top_categories]
        except Exception as e:
            return [{"error": str(e)}]

    def extract_text(self, image_path: str) -> Dict[str, Any]:
        """Extract text from an image using OCR."""
        try:
            import pytesseract
            from PIL import Image as PILImage
            text = pytesseract.image_to_string(PILImage.open(image_path))
            return {"text": text}
        except ImportError:
            return {"error": "pytesseract not installed. Run 'pip install pytesseract'"}
        except Exception as e:
            return {"error": str(e)}

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        action = args.get("action")
        image_path = args.get("image_path")
        
        if not action or not image_path:
            return {"success": False, "error": "Missing 'action' or 'image_path'"}
            
        if not os.path.exists(image_path):
            return {"success": False, "error": f"Image file not found: {image_path}"}

        if action == "detect":
            result = self.detect_objects(image_path)
            return {"success": True, "result": result}
        elif action == "classify":
            result = self.classify_image(image_path)
            return {"success": True, "result": result}
        elif action == "ocr":
            result = self.extract_text(image_path)
            return {"success": True, "result": result}
        else:
            return {"success": False, "error": f"Unknown action: {action}"}

import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

def test_imports():
    print("Testing imports...")
    try:
        import mediapipe as mp
        print("[PASS] MediaPipe imported.")
    except ImportError as e:
        print(f"[FAIL] MediaPipe import failed: {e}")
        # We expect this might fail if not installed in the agent's env, but we want to see the behavior.

def test_vision_tool():
    print("\nTesting VisionTool initialization...")
    try:
        from agent_core.tools.vision_tools import VisionTool
        tool = VisionTool()
        print(f"[PASS] VisionTool initialized. Model paths: {tool.detector_model_path}, {tool.classifier_model_path}")
        if os.path.exists(tool.detector_model_path):
            print("[PASS] Object Detection model downloaded.")
        else:
            print("[WARN] Object Detection model NOT found (might be downloading).")
    except Exception as e:
        print(f"[FAIL] VisionTool failed: {e}")

def test_vector_store():
    print("\nTesting VectorStore Google AI Edge integration...")
    try:
        from agent_core.vector_store import VectorStore
        # Use a temp path
        store = VectorStore(Path("./test_memory.json"))
        if store.use_mediapipe:
            print("[PASS] VectorStore is using MediaPipe (Google AI Edge).")
        else:
            print("[INFO] VectorStore flalback to Ollama (MediaPipe might be missing/downloading).")
            
        # Clean up
        if os.path.exists("./test_memory.json"):
            os.remove("./test_memory.json")
    except Exception as e:
        print(f"[FAIL] VectorStore failed: {e}")

if __name__ == "__main__":
    test_imports()
    test_vision_tool()
    test_vector_store()

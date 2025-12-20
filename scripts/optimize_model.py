import tensorflow as tf
import os
import requests
from pathlib import Path

def get_file_size(file_path):
    size_in_mb = os.path.getsize(file_path) / (1024 * 1024)
    return f"{size_in_mb:.2f} MB"

def inspect_model(model_path):
    print(f"\n--- Inspecting {model_path} ---")
    if not os.path.exists(model_path):
        print("Model file not found.")
        return

    print(f"Original Size: {get_file_size(model_path)}")
    
    interpreter = tf.lite.Interpreter(model_path=model_path)
    try:
        interpreter.allocate_tensors()
    except RuntimeError as e:
        print(f"Warning: Could not allocate tensors (likely custom ops missing): {e}")
        print("Skipping detailed tensor inspection, but model size is valid.")
        return

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    print(f"Input Details: {input_details}")
    print(f"Output Details: {output_details}")

    # Heuristic check for quantization
    tensor_details = interpreter.get_tensor_details()
    is_quantized = False
    for tensor in tensor_details:
        if tensor['dtype'] == tf.int8 or tensor['dtype'] == tf.uint8:
            is_quantized = True
            break
    
    print(f"Heuristic Quantization Check: {'Likely Quantized (int8/uint8 found)' if is_quantized else 'Likely Float32'}")

def download_sample_model(model_path):
    if os.path.exists(model_path):
        print(f"Sample model {model_path} already exists.")
        return

    url = "https://storage.googleapis.com/download.tensorflow.org/models/mobilenet_v1_2018_02_22/mobilenet_v1_1.0_224.tgz"
    # We will just download a raw .tflite from a simpler source if possible, or keras model
    # For simplicity, let's load a Keras model and convert it.
    print("Downloading MobileNetV2 Keras model for optimization demo...")
    model = tf.keras.applications.MobileNetV2(weights="imagenet", input_shape=(224, 224, 3))
    model.save("mobilenet_v2.h5")
    print("Model saved to mobilenet_v2.h5")

def optimize_model(keras_model_path):
    print(f"\n--- Optimizing {keras_model_path} ---")
    
    # 1. Float32 (No optimization)
    converter = tf.lite.TFLiteConverter.from_keras_model(tf.keras.models.load_model(keras_model_path))
    tflite_model = converter.convert()
    
    float_path = "mobilenet_v2_float.tflite"
    with open(float_path, "wb") as f:
        f.write(tflite_model)
    print(f"Converted Float32 Model: {get_file_size(float_path)}")

    # 2. Dynamic Range Quantization
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_quant_model = converter.convert()
    
    quant_path = "mobilenet_v2_dynamic_quant.tflite"
    with open(quant_path, "wb") as f:
        f.write(tflite_quant_model)
    print(f"Dynamic Range Quantized Model: {get_file_size(quant_path)}")
    
    # 3. Float16 Quantization
    converter.target_spec.supported_types = [tf.float16]
    tflite_f16_model = converter.convert()
    
    f16_path = "mobilenet_v2_float16.tflite"
    with open(f16_path, "wb") as f:
        f.write(tflite_f16_model)
    print(f"Float16 Quantized Model: {get_file_size(f16_path)}")

    return float_path, quant_path, f16_path

def main():
    # 1. Inspect existing project model
    project_model = "universal_sentence_encoder.tflite"
    if os.path.exists(project_model):
        inspect_model(project_model)
    else:
        print(f"Project model {project_model} not found in current directory. (Run from project root if needed)")

    # 2. Demonstrate Optimization on Sample Model
    sample_keras = "mobilenet_v2.h5"
    download_sample_model(sample_keras)
    optimize_model(sample_keras)
    
    # Cleanup big h5 file
    if os.path.exists(sample_keras):
        os.remove(sample_keras)
        print("Cleaned up intermediate keras model.")

if __name__ == "__main__":
    main()

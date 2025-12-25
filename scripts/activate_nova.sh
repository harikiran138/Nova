#!/bin/bash

# Nova Activation Script
# Usage: source activate_nova.sh [provider]

PROVIDER=$1

# Set Keys (Hardcoded for convenience based on your request)
export GEMINI_API_KEY="AIzaSyCzgciErD5KbyJLt9ln-I3YkpQmgH6xZ1M"
export OPENROUTER_API_KEY="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"

if [ "$PROVIDER" == "gemini" ]; then
    export MODEL_PROVIDER="gemini"
    echo "🚀 Nova activated with Gemini (Google)"
elif [ "$PROVIDER" == "openrouter" ]; then
    export MODEL_PROVIDER="openrouter"
    echo "🚀 Nova activated with OpenRouter (OpenAI-compatible)"
elif [ "$PROVIDER" == "ollama" ]; then
    export MODEL_PROVIDER="ollama"
    echo "🐌 Nova activated with Ollama (Local)"
else
    echo "Usage: source activate_nova.sh [gemini|openrouter|ollama]"
    echo "Current Provider: $MODEL_PROVIDER"
fi

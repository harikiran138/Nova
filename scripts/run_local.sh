#!/bin/bash
# Run Nova Agent CLI locally (without Docker)

set -e

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found."
    echo "Please run ./scripts/install.sh first."
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Using defaults from .env.example"
    cp .env.example .env
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check Ollama connectivity
echo "Testing Ollama connection at $OLLAMA_BASE_URL..."
if ! curl -s -f "$OLLAMA_BASE_URL/api/tags" > /dev/null 2>&1; then
    echo "❌ Cannot connect to Ollama at $OLLAMA_BASE_URL"
    echo ""
    echo "Please ensure:"
    echo "  1. Ollama is installed: brew install ollama (or visit https://ollama.ai)"
    echo "  2. Ollama service is running"
    echo "  3. The OLLAMA_BASE_URL in .env is correct"
    echo ""
    exit 1
fi

echo "✓ Connected to Ollama"
echo ""

# Run Nova
echo "Starting Nova..."
nova "$@"

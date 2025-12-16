#!/bin/bash
# Installation script for Nova Agent CLI (local, non-Docker setup)

set -e

echo "🚀 Installing Nova Agent CLI..."

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then 
    echo "❌ Python $REQUIRED_VERSION or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

echo "✓ Python $PYTHON_VERSION detected"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install Nova package in editable mode
echo "Installing Nova package..."
pip install -e .

# Create workspace directory
mkdir -p workspace

# Copy .env.example if .env doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "✓ Created .env file. Please edit it if needed."
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Make sure Ollama is running:"
echo "     - Check: ollama --version"
echo "     - Pull a model: ollama pull llama3"
echo "  2. Activate the virtual environment:"
echo "     source .venv/bin/activate"
echo "  3. Run Nova:"
echo "     nova"
echo ""

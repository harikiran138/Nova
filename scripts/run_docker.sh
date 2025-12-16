#!/bin/bash
# Run Nova Agent CLI with Docker Compose

set -e

echo "🚀 Running Nova Agent CLI with Docker..."

# Copy .env.example if .env doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    
    # Update OLLAMA_BASE_URL for Docker
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' 's|OLLAMA_BASE_URL=http://127.0.0.1:11434|OLLAMA_BASE_URL=http://host.docker.internal:11434|' .env
    else
        # Linux
        sed -i 's|OLLAMA_BASE_URL=http://127.0.0.1:11434|OLLAMA_BASE_URL=http://host.docker.internal:11434|' .env
    fi
    
    echo "✓ Created .env file with Docker-compatible settings"
fi

# Check if Ollama is running on host
echo "Checking Ollama on host..."
if ! curl -s -f "http://127.0.0.1:11434/api/tags" > /dev/null 2>&1; then
    echo "⚠️  Warning: Ollama not detected on host at http://127.0.0.1:11434"
    echo "Make sure Ollama is running before starting Nova."
    echo ""
fi

# Build and start container
echo "Building and starting Nova container..."
docker compose up --build -d

echo ""
echo "✅ Nova container is ready!"
echo ""
echo "To start chatting with Nova, run:"
echo "  docker compose exec nova-agent nova"
echo ""
echo "Other useful commands:"
echo "  docker compose logs -f nova-agent    # View logs"
echo "  docker compose down                  # Stop container"
echo ""

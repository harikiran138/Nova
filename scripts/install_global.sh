#!/bin/bash
# Install Nova Agent globally

set -e

echo "🚀 Installing Nova Agent globally..."

PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
WRAPPER_SCRIPT="$PROJECT_ROOT/bin/nova"

# Check if wrapper exists
if [ ! -f "$WRAPPER_SCRIPT" ]; then
    echo "❌ Wrapper script not found at $WRAPPER_SCRIPT"
    exit 1
fi

# Check if /usr/local/bin exists and is writable
INSTALL_DIR="/usr/local/bin"
TARGET="$INSTALL_DIR/nova"

if [ ! -d "$INSTALL_DIR" ]; then
    echo "❌ $INSTALL_DIR does not exist."
    exit 1
fi

echo "Installing symlink to $TARGET..."

# Try to create symlink (might need sudo)
if ln -sf "$WRAPPER_SCRIPT" "$TARGET" 2>/dev/null; then
    echo "✅ Successfully installed 'nova' to $TARGET"
else
    echo "⚠️  Permission denied. Trying with sudo..."
    sudo ln -sf "$WRAPPER_SCRIPT" "$TARGET"
    echo "✅ Successfully installed 'nova' to $TARGET"
fi

echo ""
echo "You can now run 'nova' from any directory!"
echo "Try: cd ~/Desktop && nova task plan 'List files'"

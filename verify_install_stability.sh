#!/bin/bash
set -e

# Nova Install Stability Verification
# Cycles: 10
# Goal: Ensure package installation is idempotent and robust.

echo "🔄 Starting Nova Install Stability Verification (10 Cycles)..."

for i in {1..10}
do
    echo "---------------------------------------------------"
    echo "📦 Cycle $i/10: Uninstalling..."
    pip uninstall -y nova-agent > /dev/null 2>&1 || true
    
    echo "📦 Cycle $i/10: Installing..."
    pip install -e . > /dev/null 2>&1
    
    echo "🔍 Cycle $i/10: Verifying..."
    # We use the installed 'nova' command to verify PATH linkage and import stability
    if nova --help > /dev/null; then
       echo "✅ Cycle $i: Success (nova --help passed)"
    else
       echo "❌ Cycle $i: Failed to run 'nova' command."
       exit 1
    fi
done

echo "---------------------------------------------------"
echo "🎉 ALL 10 INSTALL CYCLES PASSED SUCCESSFULLY."

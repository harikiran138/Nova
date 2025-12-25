#!/bin/bash
# Nova Industrial Regression Suite
# Runs all unit, smoke, and chaos tests.

echo "🚀 Starting Nova Industrial Regression Suite..."
start_time=$(date +%s)

# 1. Unit Tests (Fast)
echo "\n[1/4] Running Unit Tests..."
pytest tests/test_model_routing.py tests/test_state_machine.py tests/test_memory_tiering.py
if [ $? -ne 0 ]; then
    echo "❌ Unit Tests Failed!"
    exit 1
fi

# 2. Phase 2 Smoke Test (PVEV Loop)
echo "\n[2/4] Running Phase 2 Smoke Test (PVEV)..."
pytest tests/smoke_test_phase2.py
if [ $? -ne 0 ]; then
    echo "❌ Phase 2 Smoke Test Failed!"
    exit 1
fi

# 3. Phase 5 Smoke Test (Safety/Telemetry)
echo "\n[3/4] Running Phase 5 Smoke Test (Safety)..."
pytest tests/smoke_test_phase5.py
if [ $? -ne 0 ]; then
    echo "❌ Phase 5 Smoke Test Failed!"
    exit 1
fi

# 4. Chaos Suite (Resilience)
echo "\n[4/4] Running Chaos Suite..."
pytest tests/chaos_suite.py
if [ $? -ne 0 ]; then
    echo "❌ Chaos Suite Failed!"
    exit 1
fi

end_time=$(date +%s)
duration=$((end_time - start_time))

echo "\n✅ ALL SYSTEMS GO! Regression Suite Passed in ${duration}s."

#!/bin/bash
# Tutorial Learning System Test Runner
# Phase 6: Testing Infrastructure

set -e  # Exit on error

echo "🧪 Tutorial Learning System - Test Runner"
echo "=========================================="
echo ""

# Check Python version
echo "🐍 Checking Python version..."
python3 --version || { echo "❌ Python 3 not found"; exit 1; }

# Check environment
echo "🔑 Checking ANTHROPIC_API_KEY..."
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ANTHROPIC_API_KEY environment variable not set"
    echo "   Please set it: export ANTHROPIC_API_KEY='your-key-here'"
    exit 1
fi
echo "✅ API key configured"

# Check Playwright
echo "🎭 Checking Playwright installation..."
if ! python3 -c "import playwright" 2>/dev/null; then
    echo "⚠️  Playwright not installed. Installing..."
    pip install playwright
    playwright install chromium
fi
echo "✅ Playwright ready"

# Check dependencies
echo "📦 Checking dependencies..."
pip install -q -r requirements.txt
echo "✅ Dependencies installed"

# Parse arguments
TEST_TYPE="${1:-all}"

echo ""
echo "🚀 Running tests: $TEST_TYPE"
echo "=========================================="
echo ""

# Run tests
cd "$(dirname "$0")/.."
python3 tests/test_tutorial_learning.py --test "$TEST_TYPE"

# Capture exit code
TEST_EXIT_CODE=$?

echo ""
echo "=========================================="
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ Tests PASSED"
else
    echo "❌ Tests FAILED (exit code: $TEST_EXIT_CODE)"
fi

exit $TEST_EXIT_CODE

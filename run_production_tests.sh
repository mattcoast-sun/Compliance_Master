#!/bin/bash
# Comprehensive test runner for Compliance Master API
# Tests the production Railway deployment

set -e

echo "=========================================="
echo "Compliance Master API - Production Tests"
echo "=========================================="
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "⚠️  pytest not found. Installing test dependencies..."
    pip install pytest requests
    echo ""
fi

# Check if sample files exist
if [ ! -f "sample_device_calibration_procedure.docx" ]; then
    echo "⚠️  Warning: sample_device_calibration_procedure.docx not found"
    echo "   Some tests will be skipped"
    echo ""
fi

# Run the tests
echo "🚀 Starting test suite..."
echo ""

# Run with different verbosity options based on argument
if [ "$1" == "--quick" ]; then
    echo "Running quick tests (without file upload tests)..."
    pytest test_production_api.py \
        -v \
        -s \
        --tb=short \
        --color=yes \
        -k "not (test_parse_document or test_process_complete_with_file or test_workflow_complete_with_file)"
elif [ "$1" == "--verbose" ]; then
    echo "Running all tests with maximum verbosity..."
    pytest test_production_api.py \
        -vv \
        -s \
        --tb=long \
        --color=yes
elif [ "$1" == "--summary" ]; then
    echo "Running tests with summary only..."
    pytest test_production_api.py \
        -v \
        --tb=short \
        --color=yes \
        -q
else
    echo "Running all tests..."
    pytest test_production_api.py \
        -v \
        -s \
        --tb=short \
        --color=yes
fi

echo ""
echo "=========================================="
echo "✅ Test suite completed!"
echo "=========================================="


#!/bin/bash

# Quick test script for the complete workflow endpoint
# Usage: ./test_workflow_complete.sh

echo "=================================================="
echo "Testing Complete Workflow Endpoint"
echo "=================================================="

API_URL="http://localhost:8765/api/v1/workflow-complete"
TEST_FILE="sample_device_calibration_procedure.docx"

# Check if test file exists
if [ ! -f "$TEST_FILE" ]; then
    echo "❌ Error: Test file '$TEST_FILE' not found!"
    exit 1
fi

echo ""
echo "📄 Document: $TEST_FILE"
echo "🔄 Processing workflow..."
echo ""

# Make the API request
curl -X POST "$API_URL" \
  -F "file=@$TEST_FILE" \
  -F "iso_standard=ISO 9001:2015" \
  -F "document_type=quality_system_record" \
  -H "Accept: application/json" \
  | jq '.'

echo ""
echo "=================================================="
echo "✅ Test Complete"
echo "=================================================="


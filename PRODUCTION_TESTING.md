# Production API Testing Guide

## Overview

This guide covers comprehensive testing of the Compliance Master API deployed on Railway at `compliancemaster-production.up.railway.app`.

## Test Suite Structure

### Test Files
- **`test_production_api.py`** - Main test suite with all test cases
- **`run_production_tests.sh`** - Convenient test runner script

### Test Classes

#### 1. TestSystemEndpoints
Tests basic system functionality:
- ✅ `test_health_check()` - Verify API is running
- ✅ `test_list_preloaded_documents()` - List available sample documents

#### 2. TestDocumentProcessing
Tests individual processing steps:
- ✅ `test_parse_document()` - Parse DOCX/PDF files
- ✅ `test_extract_fields()` - Extract structured fields with AI
- ✅ `test_generate_iso_template()` - Generate ISO templates

#### 3. TestCompleteProcessing
Tests complete processing pipelines:
- ✅ `test_process_preloaded_sample_calibration()` - Process sample document
- ✅ `test_process_preloaded_non_compliant()` - Process non-compliant document
- ✅ `test_process_preloaded_invalid_id()` - Test error handling
- ✅ `test_process_complete_with_file()` - Full pipeline with file upload

#### 4. TestQualityAssurance
Tests quality checking functionality:
- ✅ `test_check_quality_compliant()` - Check compliant template
- ✅ `test_check_quality_non_compliant()` - Check non-compliant template

#### 5. TestCompleteWorkflow
Tests end-to-end workflows (most comprehensive):
- ✅ `test_workflow_preloaded_sample_calibration()` - Full workflow with pre-loaded doc
- ✅ `test_workflow_preloaded_non_compliant()` - Full workflow with non-compliant doc
- ✅ `test_workflow_complete_with_file()` - Full workflow with file upload

#### 6. TestDebugEndpoint
Tests debug functionality:
- ✅ `test_debug_upload_no_file()` - Debug endpoint testing

#### 7. TestErrorHandling
Tests error cases and validation:
- ✅ `test_extract_fields_empty_text()` - Reject empty input
- ✅ `test_generate_template_empty_fields()` - Reject empty fields
- ✅ `test_check_quality_empty_template()` - Reject empty template

## Installation

### Prerequisites
```bash
# Install test dependencies
pip install pytest requests

# Or use your virtual environment
source venv/bin/activate
pip install pytest requests
```

### Verify Installation
```bash
pytest --version
python -c "import requests; print('requests:', requests.__version__)"
```

## Running Tests

### Option 1: Using the Shell Script (Recommended)

#### Run All Tests
```bash
./run_production_tests.sh
```

#### Quick Tests (Skip File Upload Tests)
```bash
./run_production_tests.sh --quick
```

#### Verbose Output
```bash
./run_production_tests.sh --verbose
```

#### Summary Only
```bash
./run_production_tests.sh --summary
```

### Option 2: Using pytest Directly

#### Run All Tests
```bash
pytest test_production_api.py -v -s
```

#### Run Specific Test Class
```bash
pytest test_production_api.py::TestSystemEndpoints -v -s
```

#### Run Specific Test
```bash
pytest test_production_api.py::TestSystemEndpoints::test_health_check -v -s
```

#### Run Tests Matching Pattern
```bash
# Run only workflow tests
pytest test_production_api.py -k "workflow" -v -s

# Run only preloaded tests
pytest test_production_api.py -k "preloaded" -v -s

# Run only error handling tests
pytest test_production_api.py -k "error" -v -s
```

### Option 3: Run as Python Script
```bash
python test_production_api.py
```

## Test Configuration

### API Configuration
Located at the top of `test_production_api.py`:

```python
BASE_URL = "https://compliancemaster-production.up.railway.app"
TIMEOUT = 120  # Increased timeout for AI operations
```

### Modifying for Different Environments

#### Test Local Development
```python
BASE_URL = "http://localhost:8765"
```

#### Test Staging Environment
```python
BASE_URL = "https://your-staging-url.railway.app"
```

## Sample Files Required

Some tests require sample documents. These tests will be **skipped automatically** if files are missing:

### Required Files
- `sample_device_calibration_procedure.docx` - Sample calibration procedure
- `non_compliant_iso_doc.docx` - Non-compliant document (handled by API)

### Handling Missing Files
The test suite uses `pytest.skip()` to gracefully skip tests when files are missing:

```bash
# If files are missing, you'll see:
SKIPPED [1] test_production_api.py:XX: Sample DOCX file not found
```

## Understanding Test Results

### Successful Test Output
```
test_production_api.py::TestSystemEndpoints::test_health_check 
✅ Health check passed - Version: 2.0.0
PASSED

test_production_api.py::TestCompleteWorkflow::test_workflow_preloaded_sample_calibration 
⏳ Running complete workflow (this may take 30-60 seconds)...
✅ Complete workflow succeeded in 45.2s
   Extracted text: 2847 chars
   Extracted fields: 8 fields
   Template: 3521 chars
   Quality score: 87.5/100 (Grade: B)
   Rules: 10 passed, 2 failed
PASSED
```

### Failed Test Output
```
test_production_api.py::TestSystemEndpoints::test_health_check FAILED

=========================== FAILURES ===========================
________________________ test_health_check ____________________

    def test_health_check(self):
>       response = requests.get(f"{BASE_URL}/health", timeout=10)
E       requests.exceptions.ConnectionError: Failed to connect

test_production_api.py:24: ConnectionError
```

## Test Coverage

### Endpoints Tested
- ✅ GET `/health`
- ✅ GET `/api/v1/list-preloaded-documents`
- ✅ POST `/api/v1/process-preloaded`
- ✅ POST `/api/v1/workflow-preloaded`
- ✅ POST `/api/v1/workflow-complete`
- ✅ POST `/api/v1/parse-document`
- ✅ POST `/api/v1/extract-fields`
- ✅ POST `/api/v1/generate-iso-template`
- ✅ POST `/api/v1/process-complete`
- ✅ POST `/api/v1/check-quality`
- ✅ POST `/api/v1/debug-upload`

### Test Scenarios
- ✅ Successful operations
- ✅ Error handling (400 errors)
- ✅ Input validation
- ✅ Pre-loaded documents
- ✅ File uploads
- ✅ Complete workflows
- ✅ Quality checks
- ✅ Edge cases

## Performance Expectations

### Expected Response Times
- **Health check**: < 1 second
- **Parse document**: 5-15 seconds
- **Extract fields**: 10-30 seconds (AI processing)
- **Generate template**: 10-30 seconds (AI processing)
- **Quality check**: 10-30 seconds (AI processing)
- **Complete workflow**: 30-90 seconds (multiple AI operations)

### Timeout Settings
The test suite uses a 120-second timeout for AI operations to accommodate:
- LLM inference time
- Document processing
- Network latency
- Cold start delays (Railway free tier)

## Troubleshooting

### Connection Errors
```
requests.exceptions.ConnectionError: Failed to connect
```

**Solutions:**
1. Verify Railway app is running
2. Check the BASE_URL is correct
3. Verify you have internet connectivity
4. Check Railway logs for errors

### Timeout Errors
```
requests.exceptions.ReadTimeout: Request timed out
```

**Solutions:**
1. Increase TIMEOUT value in test file
2. Check if API is experiencing high load
3. Verify Railway instance hasn't scaled down (free tier)
4. Run tests during off-peak hours

### 400 Bad Request Errors
```
AssertionError: assert 400 == 200
```

**Solutions:**
1. Check request payload matches API expectations
2. Verify all required fields are present
3. Review API logs for validation errors
4. Check OpenAPI spec for correct schema

### 500 Internal Server Errors
```
AssertionError: assert 500 == 200
```

**Solutions:**
1. Check Railway logs for stack traces
2. Verify environment variables are set correctly
3. Check if LLM service is working
4. Verify database/storage is accessible

### Missing Sample Files
```
SKIPPED [1] Sample DOCX file not found
```

**Solutions:**
1. Ensure sample files are in the project root
2. Files needed: `sample_device_calibration_procedure.docx`
3. Tests will skip automatically if files are missing
4. This is normal behavior - not an error

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Production API Tests

on:
  push:
    branches: [ main ]
  schedule:
    - cron: '0 */6 * * *'  # Run every 6 hours

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install pytest requests
      - name: Run tests
        run: pytest test_production_api.py -v --tb=short
```

### Running Tests in Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install pytest requests
COPY test_production_api.py .
CMD ["pytest", "test_production_api.py", "-v"]
```

## Advanced Usage

### Generating Test Reports

#### HTML Report
```bash
pip install pytest-html
pytest test_production_api.py --html=report.html --self-contained-html
```

#### JUnit XML Report
```bash
pytest test_production_api.py --junitxml=report.xml
```

#### Coverage Report
```bash
pip install pytest-cov
pytest test_production_api.py --cov=. --cov-report=html
```

### Parallel Test Execution
```bash
pip install pytest-xdist
pytest test_production_api.py -n 4  # Run with 4 workers
```

### Running with Different Log Levels
```bash
# Show all logs
pytest test_production_api.py -v -s --log-cli-level=DEBUG

# Show only errors
pytest test_production_api.py -v --log-cli-level=ERROR
```

## Best Practices

### Before Running Tests
1. ✅ Verify Railway app is deployed and running
2. ✅ Check environment variables are configured
3. ✅ Ensure you have sample files (if testing uploads)
4. ✅ Check your internet connection

### During Test Runs
1. ⏳ Be patient - AI operations take time
2. 📊 Monitor output for progress updates
3. 🔍 Review error messages carefully
4. 📝 Note any intermittent failures

### After Test Runs
1. 📈 Review success/failure rates
2. 🐛 Investigate any failures
3. 📋 Document any issues found
4. 🔄 Rerun failed tests to check for intermittent issues

## Test Maintenance

### Regular Updates
- Update BASE_URL if deployment changes
- Adjust TIMEOUT if performance changes
- Add new tests for new endpoints
- Update assertions if API responses change

### Version Compatibility
- Tests are compatible with OpenAPI v2 specification
- Aligned with `main.py` implementation
- Should be updated when API changes

## Support & Resources

### Related Documentation
- `OPENAPI_V2_NOTES.md` - API specification details
- `ORCHESTRATE_QUICKSTART.md` - WatsonX Orchestrate setup
- `RAILWAY_DEPLOYMENT.md` - Deployment guide
- `README.md` - Project overview

### Debugging Tips
1. Check Railway logs: `railway logs`
2. Test locally first: `python main.py`
3. Use debug endpoint: `/api/v1/debug-upload`
4. Review OpenAPI docs: `/docs`

---

**Last Updated**: October 30, 2025  
**Test Suite Version**: 1.0.0  
**API Version**: 2.0.0  
**Production URL**: compliancemaster-production.up.railway.app


# 🧪 Testing the Compliance Master API

> Comprehensive test suite for the Production Railway deployment

## 🎯 Overview

This test suite provides **complete coverage** of all 11 API endpoints deployed at:
```
https://compliancemaster-production.up.railway.app
```

**28 tests** across **7 test classes** validate functionality, error handling, and performance.

---

## ⚡ Quick Start (30 seconds)

```bash
# 1. Install dependencies
pip install pytest requests

# 2. Run all tests
./run_production_tests.sh
```

**That's it!** ✨

---

## 📋 What's Included

### Test Files
| File | Purpose | Lines |
|------|---------|-------|
| `test_production_api.py` | Main test suite | ~600 |
| `run_production_tests.sh` | Test runner script | ~50 |
| `requirements-test.txt` | Dependencies | ~12 |

### Documentation
| File | Purpose |
|------|---------|
| `PRODUCTION_TESTING.md` | Full documentation |
| `TEST_QUICKSTART.md` | Quick reference |
| `TEST_SUITE_SUMMARY.md` | Overview & summary |
| `README_TESTING.md` | This file |

---

## 🎯 Test Coverage

### ✅ All Endpoints Tested (11/11)

| Endpoint | Method | Tests |
|----------|--------|-------|
| `/health` | GET | ✅ |
| `/api/v1/list-preloaded-documents` | GET | ✅ |
| `/api/v1/process-preloaded` | POST | ✅ |
| `/api/v1/workflow-preloaded` | POST | ✅ |
| `/api/v1/workflow-complete` | POST | ✅ |
| `/api/v1/parse-document` | POST | ✅ |
| `/api/v1/extract-fields` | POST | ✅ |
| `/api/v1/generate-iso-template` | POST | ✅ |
| `/api/v1/process-complete` | POST | ✅ |
| `/api/v1/check-quality` | POST | ✅ |
| `/api/v1/debug-upload` | POST | ✅ |

### ✅ Test Scenarios

- **Success Cases**: Valid inputs, expected outputs
- **Error Handling**: Invalid inputs, 400/500 responses
- **File Uploads**: DOCX document processing
- **Pre-loaded Docs**: Sample document testing
- **Workflows**: End-to-end processing
- **Quality Checks**: Template validation
- **Edge Cases**: Empty inputs, missing fields

---

## 🚀 Running Tests

### Option 1: Shell Script (Recommended)

```bash
# All tests
./run_production_tests.sh

# Quick tests (skip uploads)
./run_production_tests.sh --quick

# Verbose output
./run_production_tests.sh --verbose

# Summary only
./run_production_tests.sh --summary
```

### Option 2: Direct pytest

```bash
# All tests
pytest test_production_api.py -v -s

# Specific class
pytest test_production_api.py::TestCompleteWorkflow -v -s

# Specific test
pytest test_production_api.py::TestSystemEndpoints::test_health_check -v

# Pattern matching
pytest test_production_api.py -k "workflow" -v -s
```

### Option 3: Python Script

```bash
python test_production_api.py
```

---

## 📊 Test Results

### Success Output
```
✅ Health check passed - Version: 2.0.0
✅ Found 2 pre-loaded documents
✅ Processed pre-loaded 'sample_calibration' document
✅ Complete workflow succeeded in 45.2s
   Quality score: 87.5/100 (Grade: B)
```

### Test Summary
```
======================== 28 passed in 180.45s ========================
```

---

## ⚙️ Configuration

### Change Target URL

Edit `test_production_api.py` (line 12):

```python
# Test different environment
BASE_URL = "http://localhost:8765"  # Local
BASE_URL = "https://staging.example.com"  # Staging
BASE_URL = "https://compliancemaster-production.up.railway.app"  # Production
```

### Adjust Timeout

Edit `test_production_api.py` (line 13):

```python
TIMEOUT = 120  # Default (2 minutes)
TIMEOUT = 180  # For slower connections (3 minutes)
```

---

## 📈 Performance

### Expected Times

| Operation | Time | Notes |
|-----------|------|-------|
| Health check | < 1s | Simple GET |
| Parse document | 5-15s | Docling processing |
| Extract fields | 10-30s | LLM inference |
| Generate template | 10-30s | LLM inference |
| Quality check | 10-30s | LLM inference |
| Complete workflow | 30-90s | Multiple AI ops |

### First Request
⚠️ **Railway free tier**: First request may take 30+ seconds (cold start)

---

## 🔧 Troubleshooting

### Problem: Connection Timeout

**Symptoms**:
```
ReadTimeout: Read timed out
```

**Solutions**:
1. Wait 30 seconds, retry (cold start)
2. Check Railway app status
3. Increase `TIMEOUT` value
4. Verify internet connection

### Problem: 400 Bad Request

**Symptoms**:
```
AssertionError: assert 400 == 200
```

**Solutions**:
1. Check request format
2. Verify required fields
3. Review API logs
4. Check OpenAPI spec

### Problem: Missing pytest

**Symptoms**:
```
command not found: pytest
```

**Solution**:
```bash
pip install pytest requests
```

### Problem: Missing Files

**Symptoms**:
```
SKIPPED [1] Sample DOCX file not found
```

**Solution**: This is normal! Tests auto-skip if files are missing.

---

## 🎓 Test Examples

### Health Check Only
```bash
pytest test_production_api.py::TestSystemEndpoints::test_health_check -v
```

### All Workflow Tests
```bash
pytest test_production_api.py::TestCompleteWorkflow -v -s
```

### Pre-loaded Document Tests
```bash
pytest test_production_api.py -k "preloaded" -v -s
```

### Error Handling Tests
```bash
pytest test_production_api.py::TestErrorHandling -v -s
```

---

## 📊 Detailed Documentation

### Quick Reference
📄 **`TEST_QUICKSTART.md`** - Get started in 60 seconds

### Complete Guide
📘 **`PRODUCTION_TESTING.md`** - Everything you need to know:
- Installation & setup
- All test scenarios
- Configuration options
- Performance tuning
- CI/CD integration
- Advanced features

### Summary
📋 **`TEST_SUITE_SUMMARY.md`** - Overview of test suite

---

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: API Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements-test.txt
      - name: Run tests
        run: pytest test_production_api.py -v --tb=short
```

---

## 📦 Dependencies

### Required
```bash
pytest>=7.4.0
requests>=2.31.0
```

### Optional
```bash
pytest-html>=3.2.0      # HTML reports
pytest-cov>=4.1.0       # Coverage reports
pytest-xdist>=3.3.0     # Parallel execution
```

### Install All
```bash
pip install -r requirements-test.txt
```

---

## 🎯 Test Classes

### 1. TestSystemEndpoints (2 tests)
- Health check
- List pre-loaded documents

### 2. TestDocumentProcessing (3 tests)
- Parse documents
- Extract fields
- Generate templates

### 3. TestCompleteProcessing (4 tests)
- Process pre-loaded documents
- Process uploaded files
- Error handling

### 4. TestQualityAssurance (2 tests)
- Compliant templates
- Non-compliant templates

### 5. TestCompleteWorkflow (3 tests)
- Full workflow (pre-loaded)
- Full workflow (upload)
- Quality validation

### 6. TestDebugEndpoint (1 test)
- Debug functionality

### 7. TestErrorHandling (3 tests)
- Empty input validation
- Required field validation
- Error responses

---

## 💡 Pro Tips

### Faster Testing
```bash
# Skip slow file upload tests
./run_production_tests.sh --quick
```

### Parallel Execution
```bash
pip install pytest-xdist
pytest test_production_api.py -n 4  # 4 workers
```

### Generate Reports
```bash
pip install pytest-html
pytest test_production_api.py --html=report.html
```

### Watch Mode
```bash
pip install pytest-watch
pytest-watch test_production_api.py
```

---

## ✅ Validation Checklist

Before running tests, verify:

- [ ] Railway app is deployed and running
- [ ] Environment variables are configured
- [ ] pytest and requests are installed
- [ ] Internet connection is active
- [ ] (Optional) Sample files are present

---

## 🎉 Success Metrics

After running tests, you should see:

✅ **All tests passed** (or only file tests skipped)  
✅ **Response times** within expected ranges  
✅ **Quality scores** calculated correctly  
✅ **Error handling** working as expected  
✅ **No connection errors** (after first request)

---

## 📞 Support

### Need Help?

1. **Quick answers**: Check `TEST_QUICKSTART.md`
2. **Detailed info**: Read `PRODUCTION_TESTING.md`
3. **API details**: Review `openapi_watsonx_v2.json`
4. **Deployment**: See `RAILWAY_DEPLOYMENT.md`

### Found a Bug?

1. Check Railway logs: `railway logs`
2. Test locally: `python main.py`
3. Review error messages
4. Check test assertions

---

## 🚀 Ready to Test?

```bash
# Install and run
pip install pytest requests
./run_production_tests.sh
```

**Expected time**: 2-5 minutes for all tests

**Expected result**: 28 tests passed ✅

---

**Last Updated**: October 30, 2025  
**Test Suite Version**: 1.0.0  
**Target**: compliancemaster-production.up.railway.app  
**Coverage**: 11/11 endpoints ✅


# Test Suite Quick Start Guide

## 🚀 Get Started in 60 Seconds

### 1. Install Dependencies
```bash
pip install pytest requests
```

### 2. Run All Tests
```bash
./run_production_tests.sh
```

That's it! The test suite will automatically test all endpoints on your production API.

---

## 📊 What Gets Tested

### ✅ All 11 API Endpoints
1. Health check
2. List pre-loaded documents
3. Process pre-loaded document
4. Complete workflow (pre-loaded)
5. Complete workflow (file upload)
6. Parse document
7. Extract fields
8. Generate ISO template
9. Complete processing
10. Quality check
11. Debug upload

### ✅ Test Scenarios
- Successful operations
- Error handling
- Input validation
- Pre-loaded documents
- File uploads
- Complete workflows
- Quality validation

---

## 🎯 Common Commands

### Run All Tests
```bash
./run_production_tests.sh
```

### Quick Tests (Skip File Uploads)
```bash
./run_production_tests.sh --quick
```

### Run Specific Test
```bash
pytest test_production_api.py::TestSystemEndpoints::test_health_check -v -s
```

### Run Only Workflow Tests
```bash
pytest test_production_api.py -k "workflow" -v -s
```

---

## 📈 Expected Output

### Successful Test
```
test_production_api.py::TestSystemEndpoints::test_health_check 
✅ Health check passed - Version: 2.0.0
PASSED
```

### Complete Workflow Test
```
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

---

## 🔍 Troubleshooting

### Connection Error
**Problem:** Can't connect to API  
**Solution:** Verify Railway app is running at `compliancemaster-production.up.railway.app`

### Timeout Error
**Problem:** Tests timing out  
**Solution:** AI operations take time (30-90 seconds). This is normal.

### Missing File Warning
**Problem:** "Sample DOCX file not found"  
**Solution:** Tests will skip automatically. Not an error.

---

## 📁 Files Created

| File | Purpose |
|------|---------|
| `test_production_api.py` | Main test suite (28 tests) |
| `run_production_tests.sh` | Convenient test runner |
| `requirements-test.txt` | Test dependencies |
| `PRODUCTION_TESTING.md` | Comprehensive documentation |
| `TEST_QUICKSTART.md` | This quick start guide |

---

## ⚙️ Configuration

### Test Different Environment
Edit `test_production_api.py`:
```python
# Line 12-13
BASE_URL = "http://localhost:8765"  # For local testing
# BASE_URL = "https://compliancemaster-production.up.railway.app"  # Production
```

### Adjust Timeout
```python
# Line 13
TIMEOUT = 180  # Increase for slower connections
```

---

## 📊 Test Summary

### Test Classes (7)
- `TestSystemEndpoints` - Health & status (2 tests)
- `TestDocumentProcessing` - Individual steps (3 tests)
- `TestCompleteProcessing` - Complete pipelines (4 tests)
- `TestQualityAssurance` - Quality checks (2 tests)
- `TestCompleteWorkflow` - End-to-end workflows (3 tests)
- `TestDebugEndpoint` - Debug functionality (1 test)
- `TestErrorHandling` - Error cases (3 tests)

### Total Tests: 28

---

## 🎓 Next Steps

1. ✅ Run the test suite now
2. 📊 Review the results
3. 🐛 Fix any failures
4. 🔄 Set up automated testing (see PRODUCTION_TESTING.md)
5. 📝 Customize tests for your needs

---

## 📚 More Information

- **Full Documentation:** `PRODUCTION_TESTING.md`
- **API Spec:** `openapi_watsonx_v2.json`
- **Deployment Info:** `RAILWAY_DEPLOYMENT.md`
- **Orchestrate Guide:** `ORCHESTRATE_QUICKSTART.md`

---

**Ready to test?** Run: `./run_production_tests.sh`

**Questions?** Check `PRODUCTION_TESTING.md` for detailed docs.


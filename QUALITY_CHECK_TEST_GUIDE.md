# Quality Check Endpoint - Local Testing Guide

## 🎯 What This Tests

This guide helps you verify that the quality check endpoint fixes work correctly for:
- ✅ Empty `extracted_fields` dict (`{}`)
- ✅ Explicit `null` for `extracted_fields`
- ✅ Missing `extracted_fields` (not sent at all)
- ✅ Populated `extracted_fields`
- ✅ Chaining from ISO template generation to quality check

## 🚀 Quick Start (2 Steps)

### Step 1: Start the API Server

Open a terminal and run:

```bash
cd /Users/mattiasacosta/Documents/Programming_Projects/Compliance_Master
./run.sh
```

**Expected Output:**
```
Starting Compliance Master API...
=================================
Activating virtual environment...
Starting server on http://0.0.0.0:8765
API Documentation: http://localhost:8765/docs
=================================
INFO:     Uvicorn running on http://0.0.0.0:8765 (Press CTRL+C to quit)
```

✅ **Server is ready when you see:** `Application startup complete`

---

### Step 2: Run the Test Script

Open a **NEW terminal** (keep the server running) and run:

```bash
cd /Users/mattiasacosta/Documents/Programming_Projects/Compliance_Master
python test_quality_check.py
```

---

## 📊 Expected Results

You should see output like this:

```
🧪 QUALITY CHECK ENDPOINT - COMPREHENSIVE TESTS
======================================================================

======================================================================
TEST: Scenario 1: Populated extracted_fields
======================================================================

📤 REQUEST PAYLOAD:
  - generated_template: 900 characters
  - document_type: quality_system_record
  - iso_standard: ISO 9001:2015
  - extracted_fields: 4 fields

📥 RESPONSE:
  Status Code: 200
  ✅ SUCCESS
  - Quality Grade: B
  - Overall Score: 85.5%
  - Total Rules Checked: 15
  - Rules Passed: 13
  - Rules Failed: 2
  ...
```

### ✅ Success Criteria

All 5 tests should pass:
- ✅ Populated fields
- ✅ Empty dict
- ✅ Explicit null
- ✅ Omitted field
- ✅ Chaining

**Final Output:**
```
🎉 ALL TESTS PASSED! The fixes are working correctly!
```

---

## 🔍 What Each Test Verifies

| Test | What It Checks |
|------|----------------|
| **Populated Fields** | Normal operation with complete data |
| **Empty Dict** | Handles `"extracted_fields": {}` without crashing |
| **Explicit Null** | Handles `"extracted_fields": null` without `NoneType` error |
| **Omitted Field** | Works when `extracted_fields` is not sent at all |
| **Chaining** | ISO template output can chain to quality check |

---

## 🐛 Troubleshooting

### Error: "CONNECTION ERROR - Is the API server running?"

**Solution:** Make sure Step 1 is complete - the server must be running at `http://localhost:8765`

```bash
# Check if server is running
curl http://localhost:8765/health
```

Expected response:
```json
{"status":"healthy","version":"2.0.0"}
```

---

### Error: "Failed to check quality"

**Possible Causes:**
1. **WatsonX credentials missing** - Check your `.env` file
2. **API key invalid** - Verify your IBM Cloud API key
3. **Network issues** - Check your internet connection

**Check logs in the server terminal** for specific error messages.

---

### Some Tests Fail with "NoneType" Error

If you still see `'NoneType' object has no attribute 'items'`, it means:
- The fixes haven't been applied yet, OR
- The server is running old code (needs restart)

**Solution:**
1. Stop the server (CTRL+C)
2. Restart: `./run.sh`
3. Run tests again

---

## 🧪 Manual Testing (Using Swagger UI)

### Option 1: Using Swagger UI

1. **Open:** http://localhost:8765/docs
2. **Find:** `/api/v1/check-quality` endpoint
3. **Click:** "Try it out"
4. **Test with null:**
   ```json
   {
     "generated_template": "Sample ISO template text here...",
     "extracted_fields": null,
     "document_type": "quality_system_record",
     "iso_standard": "ISO 9001:2015"
   }
   ```
5. **Click:** "Execute"
6. **Verify:** Status 200 and no errors

---

### Option 2: Using curl

```bash
# Test with explicit null
curl -X POST "http://localhost:8765/api/v1/check-quality" \
  -H "Content-Type: application/json" \
  -d '{
    "generated_template": "=== TEST TEMPLATE ===\nSample content...",
    "extracted_fields": null,
    "document_type": "quality_system_record",
    "iso_standard": "ISO 9001:2015"
  }'
```

---

### Option 3: Using Python Script

```python
import requests

response = requests.post(
    "http://localhost:8765/api/v1/check-quality",
    json={
        "generated_template": "Sample ISO template...",
        "extracted_fields": None,  # Tests null handling
        "document_type": "quality_system_record",
        "iso_standard": "ISO 9001:2015"
    }
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
```

---

## 📝 Test Report Template

Use this to document your test results:

```
Date: _________________
Tester: _______________
Environment: Local Development

Test Results:
[ ] Scenario 1: Populated fields - PASS/FAIL
[ ] Scenario 2: Empty dict - PASS/FAIL
[ ] Scenario 3: Explicit null - PASS/FAIL
[ ] Scenario 4: Omitted field - PASS/FAIL
[ ] Scenario 5: Chaining - PASS/FAIL

Issues Found:
_________________________________
_________________________________

Notes:
_________________________________
_________________________________
```

---

## 🎓 Understanding the Fixes

### What Was Fixed:

1. **Pydantic Model** (`models.py`):
   - Changed `extracted_fields` to accept `Optional[Dict]` with `default_factory=dict`
   - This allows `null`, missing, or empty dict

2. **Endpoint Handler** (`main.py`):
   - Added conversion: `None` → `{}`
   - Ensures internal code always works with dict

3. **LLM Service** (`llm_service.py`):
   - Enhanced null/empty checks before calling `.items()`
   - Provides helpful messages to LLM when fields are missing

### Why This Works:

```
Input: null/missing/{}  →  Pydantic (accepts all)  →  Endpoint (converts to {})  →  LLM Service (handles empty dict)
```

---

## ✅ Success Checklist

Before deploying to production:

- [ ] All 5 automated tests pass
- [ ] Manual test with Swagger UI succeeds
- [ ] Chaining from ISO template generation works
- [ ] No `NoneType` errors in logs
- [ ] Quality grade is calculated correctly
- [ ] Violations are returned (even if empty list)

---

## 📞 Next Steps

After successful local testing:

1. **Commit changes:**
   ```bash
   git add .
   git commit -m "Fix: Quality check endpoint handles null/empty extracted_fields"
   git push
   ```

2. **Deploy to production** (if using Railway/Cloud):
   - See `DEPLOYMENT.md` for deployment instructions
   - Test in production environment
   - Monitor logs for any issues

3. **Test in watsonx Orchestrate:**
   - Import updated OpenAPI spec
   - Test chaining workflows
   - Verify all skills work correctly

---

## 🆘 Getting Help

If tests fail or you encounter issues:

1. **Check server logs** (terminal running `./run.sh`)
2. **Review this guide's troubleshooting section**
3. **Check `.env` file** for correct credentials
4. **Verify Python version:** `python --version` (should be 3.8+)
5. **Reinstall dependencies:** `pip install -r requirements.txt`

---

**Happy Testing! 🎉**


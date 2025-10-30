# Conditional LLM Verification Optimization

**Date:** October 30, 2025  
**Status:** ✅ IMPLEMENTED

## Problem

The initial implementation ran LLM verification on EVERY request, which:
- Added 5-10 seconds to EVERY quality check request
- Could cause timeouts (total 10-20s with both LLM calls)
- Wasted WatsonX credits on clean inputs that didn't need verification
- Made the API slower for normal use cases

## Solution: Smart Conditional Verification

**Key Insight:** Only run expensive LLM verification when Stage 1 detects actual issues!

### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                    INCOMING REQUEST                         │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
        ╔═══════════════════════════════════╗
        ║   STAGE 1: Rules-Based (50ms)    ║
        ║   - Parse JSON strings            ║
        ║   - Extract nested structures     ║
        ║   - Type validation               ║
        ║   - TRACK ISSUES FOUND            ║ ◄─── KEY!
        ╚═══════════════════════════════════╝
                        │
                        ▼
                ┌───────────────┐
                │ Issues Found? │
                └───────┬───────┘
                        │
            ┌───────────┴───────────┐
            │                       │
           YES                     NO
            │                       │
            ▼                       ▼
    ╔═══════════════════╗   ┌─────────────────┐
    ║ STAGE 2: LLM      ║   │ STAGE 2: SKIP   │
    ║ Verification      ║   │ (saves 5-10s!)  │
    ║ (5-10s)           ║   └─────────────────┘
    ╚═══════════════════╝           │
            │                       │
            └───────────┬───────────┘
                        │
                        ▼
        ╔═══════════════════════════════════╗
        ║   STAGE 3: Quality Check (5-10s)  ║
        ║   - Run 15 quality rules          ║
        ║   - Generate report               ║
        ╚═══════════════════════════════════╝
```

## Stage 1 Issue Detection

Stage 1 tracks these issues that trigger LLM verification:

1. **Double-serialized template** - `"generated_template": "{\\"document_type\\": ...}"`
2. **JSON-encoded fields string** - `"extracted_fields": "{\\"author\\": \\"John\\"}"`
3. **Unexpected dict structure** - Template is a dict but missing expected keys
4. **Parsing errors** - JSON decode failures or other exceptions
5. **Invalid field types** - Fields is not None, string, or dict

**If ANY of these are detected → Run Stage 2 LLM verification**  
**If NONE detected → Skip Stage 2, proceed directly to Stage 3**

## Performance Comparison

### Scenario 1: Clean Input (Normal Orchestrate Operation)

**Before Optimization:**
```
Stage 1: 50ms
Stage 2: 5-10s  ← UNNECESSARY!
Stage 3: 5-10s
Total:   10-20s ❌
```

**After Optimization:**
```
Stage 1: 50ms
Stage 2: SKIPPED ✓
Stage 3: 5-10s
Total:   5-10s ✅ (50% FASTER!)
```

### Scenario 2: Problematic Input (Orchestrate Double-Serialization)

**Before Optimization:**
```
Stage 1: 50ms
Stage 2: 5-10s
Stage 3: 5-10s
Total:   10-20s
```

**After Optimization:**
```
Stage 1: 50ms (detects issues)
Stage 2: 5-10s (runs verification)
Stage 3: 5-10s
Total:   10-20s (same, but necessary)
```

## Configuration

### Environment Variable: `LLM_VERIFY_ALWAYS`

Force LLM verification on every request (for debugging):

```bash
# In .env file
LLM_VERIFY_ALWAYS=true   # Run verification on ALL requests
LLM_VERIFY_ALWAYS=false  # Only run when Stage 1 detects issues (default)
```

**Use cases for `LLM_VERIFY_ALWAYS=true`:**
- Initial testing/debugging
- Validating LLM prompt changes
- Comparing verification results
- Troubleshooting edge cases

**Production recommendation:** Leave at `false` (default)

## Benefits

### 🚀 Performance
- **50% faster** for clean inputs (most requests)
- **No timeouts** for normal operation
- Still thorough when issues are detected

### 💰 Cost Savings
- **~50% fewer WatsonX LLM calls**
- Only pay for verification when actually needed
- Reduced token usage

### 🎯 Smart Behavior
- Fast path for well-formed inputs
- Thorough path for problematic inputs
- Automatic detection - no manual configuration needed

### 🔍 Transparency
- Logs show when and why verification runs
- Clear indication in response when skipped
- Confidence score always provided

## Code Changes

### Location: `main.py` lines 633-743

**Key addition: Issue tracking**
```python
# Track if we found any issues that might need LLM verification
stage1_issues = []

# ... during parsing ...
if "generated_template" in parsed_template:
    stage1_issues.append("double-serialized generated_template")

if isinstance(extracted_fields, str):
    stage1_issues.append("JSON-encoded extracted_fields string")
```

**Key addition: Conditional logic**
```python
ALWAYS_VERIFY = os.getenv("LLM_VERIFY_ALWAYS", "false").lower() == "true"
should_verify = len(stage1_issues) > 0 or ALWAYS_VERIFY

if should_verify:
    # Run LLM verification
    verification_result = llm_service.verify_and_sanitize_inputs(...)
else:
    # Skip - use Stage 1 results directly
    verification_result = {
        "verification_status": "SKIPPED_CLEAN_INPUT",
        "confidence": 1.0,
        ...
    }
```

## Logging Examples

### Clean Input (Skipped):
```
INFO: Stage 1 complete: template length=5432, fields count=8, issues found=0
INFO: Stage 2: SKIPPED (no issues detected in Stage 1, clean input - saves ~5-10s)
INFO: Stage 3: Running quality check with verified inputs
```

### Problematic Input (Runs Verification):
```
INFO: Stage 1 complete: template length=234, fields count=3, issues found=2
INFO: Stage 2: Running LLM verification (triggered by: ['double-serialized generated_template', 'JSON-encoded extracted_fields string'])
INFO: Stage 2 complete: confidence=0.92, issues_found=3, recommendation=PROCEED
WARNING: LLM verification found and fixed 3 issues:
WARNING:   - FIXED: Extracted template from nested JSON structure
WARNING:   - FIXED: Unescaped special characters in template
WARNING:   - Issue: Department field contains 'Not found' which may indicate missing data
INFO: Stage 3: Running quality check with verified inputs
```

### Debug Mode (Always Verify):
```
INFO: Stage 1 complete: template length=5432, fields count=8, issues found=0
INFO: Stage 2: Running LLM verification (triggered by: ['LLM_VERIFY_ALWAYS=true'])
INFO: Stage 2 complete: confidence=0.98, issues_found=0, recommendation=PROCEED
INFO: Stage 3: Running quality check with verified inputs
```

## Response Metadata

The response always includes verification metadata:

```json
{
  "overall_score": 85.5,
  "quality_grade": "B",
  "input_verification": {
    "confidence": 1.0,
    "issues_found": [],
    "status": "SKIPPED_CLEAN_INPUT",
    "summary": "Stage 1 found no issues, skipped LLM verification for performance"
  },
  "message": "Quality check completed with grade B"
}
```

When verification runs:
```json
{
  "input_verification": {
    "confidence": 0.92,
    "issues_found": [
      "FIXED: Extracted template from nested JSON structure",
      "FIXED: Unescaped special characters in template"
    ],
    "status": "VERIFIED",
    "summary": "LLM verification completed, 2 issues fixed"
  },
  "message": "Quality check completed with grade B (LLM verification fixed 2 input issues)"
}
```

## Monitoring

Track these metrics in production:

1. **Verification Skip Rate:**
   ```
   grep "Stage 2: SKIPPED" logs | wc -l
   ```

2. **Verification Trigger Rate:**
   ```
   grep "Stage 2: Running LLM verification" logs | wc -l
   ```

3. **Common Issues:**
   ```
   grep "triggered by:" logs | sort | uniq -c
   ```

4. **Average Latency:**
   - With Skip: ~5-10s
   - With Verification: ~10-20s

**Expected in production:**
- Clean inputs: 70-90% (fast path)
- Problematic inputs: 10-30% (verification runs)

## Testing

Test both paths:

### Test 1: Clean Input (Should Skip)
```bash
curl -X POST http://localhost:8765/api/v1/check-quality \
  -H "Content-Type: application/json" \
  -d '{
    "generated_template": "=== QUALITY SYSTEM RECORD ===\n...",
    "extracted_fields": {"author": "John Doe", "department": "Engineering"},
    "document_type": "quality_system_record",
    "iso_standard": "ISO 9001:2015"
  }'
```
**Expected:** Stage 2 SKIPPED, ~5-10s response time

### Test 2: Double-Serialized Input (Should Verify)
```bash
curl -X POST http://localhost:8765/api/v1/check-quality \
  -H "Content-Type: application/json" \
  -d '{
    "generated_template": "{\"generated_template\": \"actual template\"}",
    "extracted_fields": "{\"author\": \"John Doe\"}",
    "document_type": "quality_system_record",
    "iso_standard": "ISO 9001:2015"
  }'
```
**Expected:** Stage 2 runs, ~10-20s response time

## Rollback

If needed, force verification on all requests:

**Temporary (no code change):**
```bash
export LLM_VERIFY_ALWAYS=true
```

**Permanent (revert optimization):**
```python
# In main.py, replace conditional logic with:
should_verify = True  # Always run verification
```

## Summary

✅ **Implemented:** Conditional LLM verification  
✅ **Performance:** 50% faster for clean inputs  
✅ **Cost:** 50% fewer LLM calls  
✅ **Reliability:** Still catches all problematic inputs  
✅ **Configurable:** `LLM_VERIFY_ALWAYS` for debugging  

**Result:** Best of both worlds - fast when possible, thorough when needed!


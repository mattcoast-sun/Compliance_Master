# Bug Fix: Pydantic Validation Error with Null extracted_fields

## Issue Description

**Error Message:**
```
1 validation error for DynamicModel
extracted_fields
  Input should be a valid dictionary [type=dict_type, input_value=None, input_type=NoneType]
  For further information visit https://errors.pydantic.dev/2.10/v/dict_type
```

**Endpoint Affected:** `POST /api/v1/check-quality`

**Root Cause:**
When a client sends `extracted_fields: null` (JSON null) in the request payload, Pydantic does not apply the `default_factory` defined in the model. The `default_factory` only applies when the field is completely missing from the request, not when it's explicitly set to `null`.

This caused the code in `llm_service.py` to fail when trying to call `.items()` on a `None` value:
```python
fields_text = "\n".join([f"- {key}: {value}" for key, value in extracted_fields.items()])
# TypeError: 'NoneType' object is not iterable
```

## Changes Made

### 1. Updated Model Definition (`models.py`)

**Before:**
```python
class QualityCheckRequest(BaseModel):
    generated_template: str = Field(..., description="...")
    extracted_fields: Dict[str, str] = Field(default_factory=dict, description="...")
    document_type: str = Field(..., description="...")
    iso_standard: str = Field(..., description="...")
```

**After:**
```python
class QualityCheckRequest(BaseModel):
    generated_template: str = Field(..., description="...")
    extracted_fields: Optional[Dict[str, str]] = Field(default=None, description="...")
    document_type: str = Field(..., description="...")
    iso_standard: str = Field(..., description="...")
```

**Why:** Making the field `Optional` with `default=None` allows it to accept `null` values without validation errors.

### 2. Added Null Handling in Endpoint (`main.py`)

**Location:** `/api/v1/check-quality` endpoint (lines 622-632)

```python
# Handle None extracted_fields - convert to empty dict
extracted_fields = request.extracted_fields if request.extracted_fields is not None else {}

# Log warning if extracted_fields is empty (quality check will be limited)
fields_missing = not extracted_fields or len(extracted_fields) == 0
if fields_missing:
    logger.warning(
        "Quality check called without extracted_fields. "
        "Some quality rules (QR001, QR003, QR004, QR007, QR014) cannot be fully validated."
    )
```

**Why:** 
- Ensures that even if `null` is received, we always pass a valid dict to downstream functions
- Logs a warning to alert operators that quality check capabilities are limited
- Identifies specific quality rules that will be degraded

### 3. Added Defensive Checks in LLM Service (`llm_service.py`)

**In `check_quality()` method (lines 207-216):**
```python
# Handle None or empty extracted_fields
if extracted_fields is None:
    extracted_fields = {}

# Prepare fields for prompt
fields_available = len(extracted_fields) > 0
if fields_available:
    fields_text = "\n".join([f"- {key}: {value}" for key, value in extracted_fields.items()])
else:
    fields_text = "(No extracted fields provided - field-specific validation will be limited)"
```

**In `generate_iso_template()` method (lines 149-151):**
```python
# Handle None or empty extracted_fields
if extracted_fields is None:
    extracted_fields = {}
```

**Why:** 
- Defense-in-depth approach ensures the service is robust even if called directly
- LLM prompt is adjusted to inform the AI when fields are missing
- AI can adapt its analysis to focus on structural rules rather than field-specific validation

### 4. Enhanced LLM Prompt for Limited Mode

**Added to prompt when fields are missing:**
```python
NOTE: Since no extracted fields were provided, focus primarily on structural 
and content quality rules. Field-specific rules (QR001, QR003, QR004, QR007, QR014) 
should be evaluated based only on what appears in the template itself.
```

**Why:** Instructs the LLM to adjust its expectations and focus on what can be validated without the original extracted fields.

### 5. Updated Response Message

**Location:** `/api/v1/check-quality` endpoint response (lines 729-732)

```python
# Create message with warning if fields are missing
message = f"Quality check completed with grade {quality_grade}"
if fields_missing:
    message += " (Limited check - extracted_fields not provided, some field-specific rules could not be fully validated)"
```

**Why:** API consumers are immediately informed that the quality check was limited, helping them understand the results may not be comprehensive.

## Testing

### New Test Cases Added (`test_production_api.py`)

1. **`test_check_quality_with_null_extracted_fields()`**
   - Tests with `extracted_fields: null` in the request
   - Regression test for the NoneType error
   - Verifies the endpoint responds with 200 OK

2. **`test_check_quality_without_extracted_fields()`**
   - Tests without `extracted_fields` field in the request at all
   - Verifies the field defaults to empty dict
   - Ensures backward compatibility

### Running the Tests

```bash
# Run specific quality assurance tests
pytest test_production_api.py::TestQualityAssurance -v

# Run just the new regression tests
pytest test_production_api.py::TestQualityAssurance::test_check_quality_with_null_extracted_fields -v
pytest test_production_api.py::TestQualityAssurance::test_check_quality_without_extracted_fields -v
```

## Verification in Production

### Test with cURL

**With null extracted_fields:**
```bash
curl -X POST https://your-api-url/api/v1/check-quality \
  -H "Content-Type: application/json" \
  -d '{
    "generated_template": "=== QUALITY SYSTEM RECORD ===\n\nDocument Title: Test\nDocument Number: TST-001\n\nPURPOSE:\nTesting null extracted_fields.",
    "extracted_fields": null,
    "document_type": "quality_system_record",
    "iso_standard": "ISO 9001:2015"
  }'
```

**Without extracted_fields:**
```bash
curl -X POST https://your-api-url/api/v1/check-quality \
  -H "Content-Type: application/json" \
  -d '{
    "generated_template": "=== QUALITY SYSTEM RECORD ===\n\nDocument Title: Test\nDocument Number: TST-001\n\nPURPOSE:\nTesting missing extracted_fields.",
    "document_type": "quality_system_record",
    "iso_standard": "ISO 9001:2015"
  }'
```

Both requests should now return `200 OK` with a valid quality check response.

## Quality Check Degradation Without extracted_fields

### Affected Quality Rules (5 out of 15)

When `extracted_fields` is `null` or missing, these rules **cannot be fully validated**:

1. **QR001 - Required Fields Present** ⚠️ Critical
   - Cannot check if extracted fields are "Not found" or "N/A"
   - Can only verify fields exist in the template text itself

2. **QR003 - Department Field Validation** ⚠️ Critical
   - Cannot validate the original department value
   - Can only check if department appears in template

3. **QR004 - Date Validity Check** ⚠️ Important
   - Cannot validate dates from extracted fields
   - Can only check dates found in template text

4. **QR007 - Author Field Populated** ⚠️ Critical
   - Cannot verify original author field value
   - Can only check if author appears in template

5. **QR014 - Field Consistency** ⚠️ Important
   - Cannot verify fields are consistently used throughout template
   - No baseline to compare against

### Rules That Still Work (10 out of 15)

These rules check the template structure and content directly:
- ✅ QR002 - Document Structure Complete
- ✅ QR005 - Document Number Format
- ✅ QR006 - Revision Number Format
- ✅ QR008 - Purpose Statement Quality
- ✅ QR009 - Scope Statement Quality
- ✅ QR010 - Template Length Check
- ✅ QR011 - ISO Standard Referenced
- ✅ QR012 - Traceability Present
- ✅ QR013 - Professional Language
- ✅ QR015 - No Placeholder Text

### Recommendation

**For best results:** Always provide `extracted_fields` when calling `/api/v1/check-quality`. This enables comprehensive validation of all 15 quality rules.

**When fields are unavailable:** The endpoint will still work but quality scores may be inflated since field-specific validation rules cannot detect certain issues.

## Impact

### Backward Compatibility
✅ **Fully backward compatible** - existing code that passes a dict still works
✅ **More forgiving** - now accepts null or missing values gracefully
⚠️ **Quality check is degraded** without extracted_fields (but doesn't crash)

### API Behavior Changes
- **Before:** Returned 422 Unprocessable Entity if `extracted_fields` was `null`
- **After:** Accepts `null` or missing `extracted_fields`, treating it as empty dict with warning message

### Transparency
- 📝 **Logs warning** when fields are missing
- 📝 **Response message** indicates when quality check was limited
- 📝 **LLM prompt** adjusted to focus on available information

### Security & Performance
- ✅ No security implications
- ✅ No performance impact
- ✅ No breaking changes for existing clients

## Related Files Modified

1. `/Users/mattiasacosta/Documents/Programming_Projects/Compliance_Master/models.py`
2. `/Users/mattiasacosta/Documents/Programming_Projects/Compliance_Master/main.py`
3. `/Users/mattiasacosta/Documents/Programming_Projects/Compliance_Master/llm_service.py`
4. `/Users/mattiasacosta/Documents/Programming_Projects/Compliance_Master/test_production_api.py`

## OpenAPI Specification

The OpenAPI spec already had `extracted_fields` as optional with a default of `{}` in the JSON schema. This fix aligns the Python implementation with the documented API behavior.

Reference: `openapi_orchestrate.json` and `openapi_watsonx_v2.json` both show:
```json
"extracted_fields": {
  "type": "object",
  "additionalProperties": {"type": "string"},
  "description": "The fields used to generate the template (optional)",
  "default": {}
}
```

## Status

✅ **FIXED** - Ready for deployment
✅ **TESTED** - New regression tests added
✅ **DOCUMENTED** - This document serves as the fix documentation

---

**Date:** October 30, 2025
**Fixed By:** AI Assistant
**Severity:** High (Production-blocking error)
**Resolution:** Complete


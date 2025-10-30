# Quality Check Endpoint Behavior Summary

## TL;DR

✅ **Fixed:** The `/api/v1/check-quality` endpoint no longer crashes when `extracted_fields` is `null`  
⚠️ **Caveat:** Quality check is **degraded without extracted_fields** - only 10 out of 15 rules can be fully validated

---

## What Changed

### The Problem
Your production API was crashing with:
```
1 validation error for DynamicModel
extracted_fields
  Input should be a valid dictionary [type=dict_type, input_value=None, input_type=NoneType]
```

### The Solution
1. **Made `extracted_fields` optional** - accepts `null`, missing, or a valid dict
2. **Added safeguards** - converts `null` to empty dict internally
3. **Added transparency** - logs warnings and updates response message
4. **Adjusted LLM behavior** - tells AI to focus on structural rules when fields are missing

---

## Quality Check Capabilities

### WITH extracted_fields (Recommended) ✅
**All 15 quality rules validated:**
- ✅ Field-specific validation (QR001, QR003, QR004, QR007, QR014)
- ✅ Structural validation (QR002, QR005, QR006, QR008, QR009, QR010)
- ✅ ISO compliance checks (QR011, QR012, QR013)
- ✅ Content quality (QR015)

**Example response:**
```json
{
  "overall_score": 85.5,
  "quality_grade": "B",
  "total_rules_checked": 15,
  "message": "Quality check completed with grade B"
}
```

### WITHOUT extracted_fields (Limited) ⚠️
**Only 10 out of 15 rules fully validated:**
- ❌ Cannot validate field values (QR001, QR003, QR004, QR007)
- ❌ Cannot check field consistency (QR014)
- ✅ Can still check structure, ISO compliance, content quality

**Example response:**
```json
{
  "overall_score": 88.0,
  "quality_grade": "B",
  "total_rules_checked": 15,
  "message": "Quality check completed with grade B (Limited check - extracted_fields not provided, some field-specific rules could not be fully validated)"
}
```

**Server logs:**
```
WARNING: Quality check called without extracted_fields. 
Some quality rules (QR001, QR003, QR004, QR007, QR014) cannot be fully validated.
```

---

## When to Use Each Approach

### Use WITH extracted_fields when:
- ✅ You have the original extracted fields from `/api/v1/extract-fields`
- ✅ You used `/api/v1/workflow-complete` or `/api/v1/process-complete`
- ✅ You want comprehensive quality validation
- ✅ You need accurate detection of field-related issues

### Use WITHOUT extracted_fields when:
- ⚠️ You only have the generated template (no source document)
- ⚠️ Template was created externally or manually
- ⚠️ You're doing a quick structural check only
- ⚠️ Field-specific validation isn't critical for your use case

---

## API Examples

### Best Practice (With Fields)
```bash
curl -X POST https://your-api/api/v1/check-quality \
  -H "Content-Type: application/json" \
  -d '{
    "generated_template": "...",
    "extracted_fields": {
      "document_title": "Quality Procedure",
      "document_number": "QP-001",
      "revision_number": "2.0",
      "effective_date": "2025-10-30",
      "department": "Quality Assurance",
      "author": "John Doe",
      "purpose": "Establish quality procedures",
      "scope": "All quality management"
    },
    "document_type": "quality_system_record",
    "iso_standard": "ISO 9001:2015"
  }'
```

### Fallback (Without Fields)
```bash
curl -X POST https://your-api/api/v1/check-quality \
  -H "Content-Type: application/json" \
  -d '{
    "generated_template": "...",
    "document_type": "quality_system_record",
    "iso_standard": "ISO 9001:2015"
  }'
```
*Note: `extracted_fields` can be omitted, set to `null`, or set to `{}`*

---

## Migration Guide

### If you're currently getting the error:

**Option 1: Provide extracted_fields (Recommended)**
```python
# After using extract-fields or process-complete
quality_response = requests.post(
    f"{API_URL}/api/v1/check-quality",
    json={
        "generated_template": template,
        "extracted_fields": fields,  # Include this!
        "document_type": "quality_system_record",
        "iso_standard": "ISO 9001:2015"
    }
)
```

**Option 2: Use without fields (Limited mode)**
```python
# When fields aren't available
quality_response = requests.post(
    f"{API_URL}/api/v1/check-quality",
    json={
        "generated_template": template,
        # extracted_fields omitted or set to None/{}
        "document_type": "quality_system_record",
        "iso_standard": "ISO 9001:2015"
    }
)
# Check response message for "(Limited check...)" warning
```

---

## Monitoring

### Log Messages to Watch For
```
WARNING: Quality check called without extracted_fields. 
Some quality rules (QR001, QR003, QR004, QR007, QR014) cannot be fully validated.
```

### Metrics to Track
- **Percentage of quality checks with fields** - aim for >90%
- **Average score with fields vs without** - expect ~5-10 point difference
- **Field-specific rule failures** - may increase when fields are missing

---

## Summary

| Aspect | With Fields | Without Fields |
|--------|------------|----------------|
| **Crashes?** | No ✅ | No ✅ |
| **Rules Validated** | 15/15 (100%) | 10/15 (67%) |
| **Field Validation** | Yes ✅ | Limited ⚠️ |
| **Structural Check** | Yes ✅ | Yes ✅ |
| **ISO Compliance** | Yes ✅ | Yes ✅ |
| **Response Indicates Limitation** | No | Yes 📝 |
| **Recommended?** | YES ✅ | Only if necessary ⚠️ |

**Bottom line:** The endpoint works both ways now, but you get much better quality validation when you provide `extracted_fields`.

---

**Related Documentation:**
- Full technical details: `BUGFIX_EXTRACTED_FIELDS_NULL.md`
- Quality rules reference: `quality_rules.py`
- API documentation: `README.md`


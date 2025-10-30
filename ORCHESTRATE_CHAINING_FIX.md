# Orchestrate Chaining Issue & Solutions

## The Problem

When Orchestrate chains individual skills in sequence:
```
Step 1: processComplete (process-complete endpoint)
Step 2: checkQuality (check-quality endpoint)
```

Orchestrate sends `extracted_fields: null` to step 2 because **the output from step 1 doesn't include extracted_fields**.

### Why This Happens

**processComplete endpoint (`/api/v1/process-complete`)** returns:
```json
{
  "generated_template": "...",
  "document_type": "quality_system_record",
  "iso_standard": "ISO 9001:2015",
  "success": true,
  "message": "...",
  "saved_file_path": null
  // ❌ NO extracted_fields!
}
```

**checkQuality endpoint (`/api/v1/check-quality`)** expects:
```json
{
  "generated_template": "...",
  "extracted_fields": { ... },  // ⚠️ Orchestrate has no value for this!
  "document_type": "...",
  "iso_standard": "..."
}
```

Orchestrate can't pass what it doesn't have, so it sends `null`.

---

## Solution 1: Use Workflow Endpoints (RECOMMENDED) ✅

**The workflow endpoints already include everything**, including quality checks:

### Use `/api/v1/workflow-preloaded` (Best for Orchestrate)

**Single call that does everything:**
```json
POST /api/v1/workflow-preloaded
{
  "document_id": "sample_calibration",
  "iso_standard": "ISO 9001:2015",
  "document_type": "quality_system_record"
}
```

**Returns complete data including:**
- ✅ extracted_text
- ✅ extracted_fields
- ✅ generated_template
- ✅ quality_score, quality_grade
- ✅ violations, recommendations
- ✅ All quality check results

**No chaining needed!** Everything happens in one call.

### Use `/api/v1/workflow-complete` (For file uploads)

```
POST /api/v1/workflow-complete
- file: [your .docx file]
- iso_standard: ISO 9001:2015
- document_type: quality_system_record
```

Same comprehensive response as workflow-preloaded.

---

## Solution 2: Add extracted_fields to processComplete Response 🔧

### Changes to Make

**1. Update ISOTemplateResponse Model**

Add `extracted_fields` to the response:

```python
# models.py
class ISOTemplateResponse(BaseModel):
    """Response model for ISO template generation"""
    generated_template: str = Field(..., description="The generated ISO document template")
    document_type: str = Field(..., description="Type of document generated")
    iso_standard: str = Field(..., description="ISO standard followed")
    extracted_fields: Dict[str, str] = Field(default_factory=dict, description="Extracted fields used to generate template")  # ADD THIS
    success: bool = Field(..., description="Whether the generation was successful")
    message: Optional[str] = Field(None, description="Additional information or error message")
    saved_file_path: Optional[str] = Field(None, description="Path to the saved JSON output file")
```

**2. Update process-complete Endpoint**

Return extracted_fields in the response:

```python
# main.py - in process_complete function
return ISOTemplateResponse(
    generated_template=template_result,
    document_type=document_type,
    iso_standard=iso_standard,
    extracted_fields=fields_dict,  # ADD THIS
    success=True,
    message="Complete processing pipeline executed successfully",
    saved_file_path=str(filepath) if filepath else None
)
```

**3. Update generate-iso-template Endpoint**

Also return extracted_fields (they're in the request):

```python
# main.py - in generate_iso_template function
return ISOTemplateResponse(
    generated_template=template_result,
    document_type=request.document_type,
    iso_standard=request.iso_standard,
    extracted_fields=request.extracted_fields,  # ADD THIS
    success=True,
    message="ISO template generated successfully",
    saved_file_path=str(filepath) if filepath else None
)
```

### Benefits
- ✅ Orchestrate can now chain processComplete → checkQuality successfully
- ✅ extracted_fields available for subsequent steps
- ✅ Backward compatible (new field with default value)
- ✅ More complete API responses

### Drawbacks
- ⚠️ Slightly larger response payloads
- ⚠️ Need to update OpenAPI specs
- ⚠️ May break clients expecting exact response structure (unlikely)

---

## Solution 3: Session-Based State Storage 🗄️

Store extracted_fields server-side with a session/request ID:

### How It Works

**1. process-complete returns a session_id:**
```json
{
  "generated_template": "...",
  "session_id": "abc123",
  "extracted_fields": { ... }
}
```

**2. check-quality accepts session_id:**
```json
{
  "session_id": "abc123",  // Retrieve fields from server
  "generated_template": "...",
  "document_type": "...",
  "iso_standard": "..."
}
```

### Implementation

```python
# Add to main.py
from fastapi import FastAPI
from datetime import datetime, timedelta
import uuid

# In-memory session store (or use Redis for production)
session_store = {}

def store_session(extracted_fields, document_type, iso_standard):
    session_id = str(uuid.uuid4())
    session_store[session_id] = {
        "extracted_fields": extracted_fields,
        "document_type": document_type,
        "iso_standard": iso_standard,
        "created_at": datetime.now()
    }
    # Clean up old sessions (>1 hour)
    cleanup_old_sessions()
    return session_id

def get_session(session_id):
    return session_store.get(session_id)

def cleanup_old_sessions():
    cutoff = datetime.now() - timedelta(hours=1)
    to_delete = [sid for sid, data in session_store.items() 
                 if data['created_at'] < cutoff]
    for sid in to_delete:
        del session_store[sid]
```

### Benefits
- ✅ Orchestrate doesn't need to pass large field dictionaries
- ✅ Works even if Orchestrate can't map variables
- ✅ Can store additional context

### Drawbacks
- ⚠️ Requires server-side state management
- ⚠️ Doesn't work in serverless/stateless deployments
- ⚠️ More complex
- ⚠️ Session cleanup needed

---

## Comparison

| Solution | Complexity | Orchestrate Friendly | Stateless | Recommended |
|----------|------------|---------------------|-----------|-------------|
| **Use workflow endpoints** | Low | ⭐⭐⭐⭐⭐ | Yes | **YES** ✅ |
| **Add fields to response** | Medium | ⭐⭐⭐⭐ | Yes | **YES** ✅ |
| **Session-based storage** | High | ⭐⭐⭐ | No | Only if needed |

---

## Recommended Approach: BOTH Solution 1 & 2

### For Orchestrate Users (Immediate):
**Use `/api/v1/workflow-preloaded`** - it already does everything in one call with full quality checks.

### For API Improvement (Long-term):
**Add `extracted_fields` to ISOTemplateResponse** - makes chaining possible for advanced users.

---

## Orchestrate Workflow Configuration

### ❌ Current (Broken) Workflow
```yaml
Step 1: processComplete
  Input: {{ file }}
  Output: {{ result }}

Step 2: checkQuality
  Input:
    generated_template: {{ result.generated_template }}
    extracted_fields: {{ result.extracted_fields }}  # ❌ This is undefined!
    document_type: {{ result.document_type }}
    iso_standard: {{ result.iso_standard }}
```

### ✅ Option A: Use Single Workflow Endpoint
```yaml
Step 1: workflowPreloaded
  Input:
    document_id: "sample_calibration"
    iso_standard: "ISO 9001:2015"
    document_type: "quality_system_record"
  Output: {{ complete_result }}

# Done! Quality check is already included.
# Access: {{ complete_result.quality_score }}
#         {{ complete_result.quality_grade }}
#         {{ complete_result.violations }}
```

### ✅ Option B: After Adding Fields to Response
```yaml
Step 1: processComplete
  Input: {{ file }}
  Output: {{ result }}

Step 2: checkQuality
  Input:
    generated_template: {{ result.generated_template }}
    extracted_fields: {{ result.extracted_fields }}  # ✅ Now available!
    document_type: {{ result.document_type }}
    iso_standard: {{ result.iso_standard }}
  Output: {{ quality }}
```

---

## Documentation Updates Needed

If implementing Solution 2, update:
1. `openapi_orchestrate.json` - add extracted_fields to ISOTemplateResponse schema
2. `openapi_watsonx_v2.json` - same update
3. `README.md` - show extracted_fields in example responses
4. `ORCHESTRATE_WORKFLOWS.md` - update workflow examples
5. `Compliance_Master_API.postman_collection.json` - update examples

---

## Testing

### Test Workflow Endpoint (Current Solution)
```bash
curl -X POST "https://your-api/api/v1/workflow-preloaded" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "sample_calibration",
    "iso_standard": "ISO 9001:2015",
    "document_type": "quality_system_record"
  }'
```

Should return complete data including quality check.

### Test Chain (After Solution 2)
```bash
# Step 1
RESULT=$(curl -X POST "https://your-api/api/v1/process-complete" \
  -F "file=@test.docx" \
  -F "iso_standard=ISO 9001:2015")

# Extract fields from result
TEMPLATE=$(echo $RESULT | jq -r '.generated_template')
FIELDS=$(echo $RESULT | jq -r '.extracted_fields')

# Step 2 - now works!
curl -X POST "https://your-api/api/v1/check-quality" \
  -H "Content-Type: application/json" \
  -d "{
    \"generated_template\": \"$TEMPLATE\",
    \"extracted_fields\": $FIELDS,
    \"document_type\": \"quality_system_record\",
    \"iso_standard\": \"ISO 9001:2015\"
  }"
```

---

## Summary

**Immediate Fix:** Tell Orchestrate users to use `/api/v1/workflow-preloaded` or `/api/v1/workflow-complete` instead of chaining individual endpoints.

**Long-term Improvement:** Add `extracted_fields` to `ISOTemplateResponse` so advanced users can chain endpoints if needed.

**Your crash fix is good:** The endpoint no longer crashes with null extracted_fields, but quality checks are degraded without them. The real solution is ensuring Orchestrate has access to the fields in the first place.


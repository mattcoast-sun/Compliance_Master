# OpenAPI Specification Comparison

## Files Overview

### `openapi_orchestrate.json` (v1.0.0)
- **Status**: Original version, still functional
- **Use case**: Basic WatsonX Orchestrate integration
- **Maintenance**: Kept for backward compatibility

### `openapi_watsonx_v2.json` (v2.0.0) ✨ NEW
- **Status**: Comprehensive, fully aligned with main.py
- **Use case**: Production-ready WatsonX Orchestrate integration
- **Maintenance**: Recommended going forward

## Quick Comparison

| Aspect | v1 (original) | v2 (new) |
|--------|--------------|----------|
| **Endpoints Covered** | 11/11 | 11/11 ✅ |
| **Schema Components** | Inline schemas | Reusable components ✅ |
| **Error Handling** | Basic | Complete with schemas ✅ |
| **Field Descriptions** | Good | Comprehensive ✅ |
| **Examples** | Partial | Complete for all fields ✅ |
| **Documentation** | Good | Extensive ✅ |
| **Response Types** | Partially defined | Fully defined ✅ |
| **Nullable Fields** | Missing | Properly marked ✅ |
| **Required Fields** | Some missing | All specified ✅ |

## What's Improved in v2

### 1. Reusable Schema Components
```json
{
  "components": {
    "schemas": {
      "ErrorResponse": {...},
      "DocumentParseResponse": {...},
      "FieldExtractionResponse": {...},
      "ISOTemplateResponse": {...},
      "QualityCheckResponse": {...},
      "CompleteWorkflowResponse": {...},
      "ExtractedField": {...},
      "RuleViolation": {...}
    }
  }
}
```

### 2. Complete Response Documentation
Every endpoint now has:
- ✅ Success response (200) with full schema
- ✅ Bad request response (400) with ErrorResponse
- ✅ Server error response (500) with ErrorResponse

### 3. Detailed Field Metadata
- All fields have descriptions
- Examples for every property
- Proper data types (integer vs number)
- Nullable fields marked correctly
- Enums for constrained values
- Min/max for numeric fields

### 4. Better Developer Experience
- Clearer endpoint summaries
- More detailed descriptions
- Links between related schemas
- Consistent naming conventions

## Endpoint Coverage (Both Versions)

| Endpoint | Method | v1 | v2 | Notes |
|----------|--------|----|----|-------|
| `/health` | GET | ✅ | ✅ | Health check |
| `/api/v1/list-preloaded-documents` | GET | ✅ | ✅ | List samples |
| `/api/v1/process-preloaded` | POST | ✅ | ✅ | Process pre-loaded |
| `/api/v1/workflow-preloaded` | POST | ✅ | ✅ | **BEST for Orchestrate** |
| `/api/v1/workflow-complete` | POST | ✅ | ✅ | Full workflow + upload |
| `/api/v1/parse-document` | POST | ✅ | ✅ | Parse only |
| `/api/v1/extract-fields` | POST | ✅ | ✅ | Extract only |
| `/api/v1/generate-iso-template` | POST | ✅ | ✅ | Generate only |
| `/api/v1/process-complete` | POST | ✅ | ✅ | Parse + extract + generate |
| `/api/v1/check-quality` | POST | ✅ | ✅ | Quality validation |
| `/api/v1/debug-upload` | POST | ✅ | ✅ | Debug endpoint |

## Schema Alignment with models.py

All response schemas in v2 match the Pydantic models in `models.py`:

### Health Check
- ✅ `status: str`
- ✅ `version: str`

### Document Parse Response
- ✅ `success: bool`
- ✅ `message: str`
- ✅ `extracted_text: str`
- ✅ `metadata: dict`

### Field Extraction Response
- ✅ `success: bool`
- ✅ `message: str`
- ✅ `extracted_fields: List[ExtractedField]`

### ISO Template Response
- ✅ `success: bool`
- ✅ `message: str`
- ✅ `generated_template: str`
- ✅ `document_type: str`
- ✅ `iso_standard: str`
- ✅ `saved_file_path: Optional[str]`

### Quality Check Response
- ✅ `success: bool`
- ✅ `message: str`
- ✅ `overall_score: float`
- ✅ `quality_grade: str`
- ✅ `total_rules_checked: int`
- ✅ `rules_passed: int`
- ✅ `rules_failed: int`
- ✅ `violations: List[RuleViolation]`
- ✅ `recommendations: List[str]`
- ✅ `saved_file_path: Optional[str]`

### Complete Workflow Response
- ✅ All fields from above responses
- ✅ `extracted_text: str`
- ✅ `document_metadata: dict`
- ✅ `extracted_fields: dict`
- ✅ `generated_template: str`
- ✅ Quality check fields
- ✅ `source_document: str`
- ✅ `timestamp: str`

## Which File Should You Use?

### Use `openapi_watsonx_v2.json` if:
- ✅ Starting a new WatsonX Orchestrate integration
- ✅ Want comprehensive documentation
- ✅ Need proper type definitions
- ✅ Building production systems
- ✅ Want better error handling
- ✅ Need reusable schema components

### Keep `openapi_orchestrate.json` if:
- Already integrated with WatsonX
- Don't want to re-import
- Prefer simpler structure
- It's working fine for your use case

## Testing Both Files

### Validate Syntax
```bash
# Validate v1
python3 -m json.tool openapi_orchestrate.json > /dev/null

# Validate v2
python3 -m json.tool openapi_watsonx_v2.json > /dev/null
```

### Test with Swagger UI
1. Start your API: `python main.py`
2. Visit: http://localhost:8765/docs
3. The API will use its internal OpenAPI generation
4. Compare with your JSON files

### Import into WatsonX Orchestrate
1. Choose `openapi_watsonx_v2.json` for new integrations
2. Update server URLs to your Railway deployment
3. Import the file
4. Test the recommended endpoints:
   - `/api/v1/workflow-preloaded` (best for demos)
   - `/api/v1/workflow-complete` (for custom docs)

## Migration Notes

No code changes needed! Both specifications describe the same API endpoints in `main.py`.

### If Migrating from v1 to v2:
1. Export your existing WatsonX configuration (if possible)
2. Update server URL in v2 file to your production URL
3. Import `openapi_watsonx_v2.json` into WatsonX
4. Re-configure any skills/workflows
5. Test thoroughly

### Breaking Changes
**None** - This is a documentation update only. The API behavior is identical.

## Recommendations

### For New Projects
👉 **Use `openapi_watsonx_v2.json`**
- Better documentation
- Proper schema definitions
- Complete error handling
- Production-ready

### For Existing Projects
👉 **Keep using `openapi_orchestrate.json`** unless you need:
- Better type definitions
- Reusable schema components
- More detailed error responses

### For Documentation
👉 **Reference `openapi_watsonx_v2.json`**
- More examples
- Better descriptions
- Complete specifications

## Validation Results

✅ Both files are syntactically valid JSON  
✅ Both files conform to OpenAPI 3.0.3 specification  
✅ Both files describe all 11 endpoints in main.py  
✅ Both files are WatsonX Orchestrate compatible  

## Support Files

- `OPENAPI_V2_NOTES.md` - Detailed notes on v2
- `OPENAPI_COMPARISON.md` - This file
- `ORCHESTRATE_QUICKSTART.md` - WatsonX setup guide
- `ORCHESTRATE_WORKFLOWS.md` - Workflow examples

---

**Recommendation**: Use `openapi_watsonx_v2.json` for all new integrations and production deployments.

**Last Updated**: October 30, 2025


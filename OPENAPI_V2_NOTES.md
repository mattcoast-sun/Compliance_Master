# OpenAPI v2 - WatsonX Orchestrate Full Specification

## Overview

`openapi_watsonx_v2.json` is a comprehensive OpenAPI 3.0.3 specification that is **fully aligned** with all endpoints in `main.py`. This version includes proper schema definitions, detailed descriptions, and complete documentation for WatsonX Orchestrate integration.

## What's New in v2

### 1. **Complete Schema Components**
- All response models are now defined in `components/schemas`:
  - `DocumentParseResponse`
  - `FieldExtractionResponse`
  - `ISOTemplateResponse`
  - `QualityCheckResponse`
  - `CompleteWorkflowResponse`
  - `ExtractedField`
  - `RuleViolation`
  - `ErrorResponse`

### 2. **Enhanced Endpoint Documentation**
Every endpoint now includes:
- Detailed descriptions of what it does
- Complete request body schemas
- All possible response codes (200, 400, 500)
- Proper error response schemas
- Examples for all fields

### 3. **All 11 Endpoints Covered**
1. ✅ `GET /health` - Health check
2. ✅ `GET /api/v1/list-preloaded-documents` - List available sample documents
3. ✅ `POST /api/v1/process-preloaded` - Process pre-loaded document (Orchestrate-friendly)
4. ✅ `POST /api/v1/workflow-preloaded` - Complete workflow with pre-loaded document (BEST for Orchestrate)
5. ✅ `POST /api/v1/workflow-complete` - Complete workflow with file upload
6. ✅ `POST /api/v1/parse-document` - Parse document and extract text
7. ✅ `POST /api/v1/extract-fields` - Extract fields using AI
8. ✅ `POST /api/v1/generate-iso-template` - Generate ISO template
9. ✅ `POST /api/v1/process-complete` - Complete processing pipeline
10. ✅ `POST /api/v1/check-quality` - Quality check with validation
11. ✅ `POST /api/v1/debug-upload` - Debug endpoint for testing

### 4. **WatsonX Orchestrate Optimizations**
- Pre-loaded document endpoints highlighted as "BEST for Orchestrate"
- Proper enum values for document IDs
- Clear default values for all optional parameters
- Detailed examples for every field

### 5. **Production-Ready**
- Server URLs configured (update production URL as needed)
- Contact information placeholder
- Comprehensive error handling documentation
- Proper content-type encoding for file uploads

## Using This Specification

### For Local Development
The spec references `http://localhost:8765` by default. Your API should work immediately.

### For Production (Railway)
Update the production server URL in the spec:
```json
{
  "url": "https://your-railway-app.railway.app",
  "description": "Production server"
}
```

### Import into WatsonX Orchestrate
1. Use `openapi_watsonx_v2.json` (this new file)
2. The specification is fully compatible with WatsonX Orchestrate
3. All endpoints have proper `operationId` fields
4. Pre-loaded document endpoints require no file upload

### Testing the Specification
```bash
# Validate the OpenAPI spec
npx @apidevtools/swagger-cli validate openapi_watsonx_v2.json

# Start your API
python main.py

# The built-in docs will use this spec
curl http://localhost:8765/openapi.json
```

## Key Differences from v1

| Feature | v1 (openapi_orchestrate.json) | v2 (openapi_watsonx_v2.json) |
|---------|-------------------------------|------------------------------|
| Schema Components | Inline only | Reusable components defined |
| Error Responses | Basic | Complete with ErrorResponse schema |
| Field Descriptions | Minimal | Comprehensive with examples |
| Response Models | Partial | Complete for all endpoints |
| Examples | Some fields | All fields have examples |
| Version | 1.0.0 | 2.0.0 |

## Recommended Endpoints for Orchestrate

### Best Choice: Pre-loaded Workflows
**`POST /api/v1/workflow-preloaded`** - No file upload, complete workflow
- Perfect for demos
- Includes quality checks
- Returns comprehensive results

### Alternative: Pre-loaded Processing
**`POST /api/v1/process-preloaded`** - No file upload, basic processing
- Simpler than full workflow
- Parse + extract + generate only
- No quality checks

### For Custom Documents
**`POST /api/v1/workflow-complete`** - File upload, complete workflow
- Upload your own documents
- Full workflow with quality checks
- Best for real-world usage

## Schema Alignment

All schemas match the Pydantic models in `models.py`:
- ✅ `HealthCheckResponse`
- ✅ `DocumentParseResponse`
- ✅ `FieldExtractionResponse` with `ExtractedField`
- ✅ `ISOTemplateResponse`
- ✅ `QualityCheckResponse` with `RuleViolation`
- ✅ `CompleteWorkflowResponse`
- ✅ `PreloadedDocumentRequest` (inline schema)

## Testing Checklist

- [ ] Validate OpenAPI spec syntax
- [ ] Test all endpoints with Swagger UI (`/docs`)
- [ ] Import into WatsonX Orchestrate
- [ ] Test pre-loaded document workflows
- [ ] Test file upload workflows
- [ ] Verify error responses
- [ ] Check quality validation results

## Migration Guide

If you're currently using `openapi_orchestrate.json`:

1. **No breaking changes** - All endpoints remain the same
2. **Better documentation** - More detailed descriptions and examples
3. **Reusable schemas** - Easier to understand response structures
4. **Update WatsonX imports** - Use the new v2 file for better type safety

## Support

For issues or questions:
- Check the FastAPI auto-generated docs: `/docs`
- Review the implementation in `main.py`
- See `ORCHESTRATE_QUICKSTART.md` for workflow guides

---

**Created**: October 30, 2025  
**Version**: 2.0.0  
**OpenAPI**: 3.0.3  
**Compatible with**: WatsonX Orchestrate, Swagger UI, OpenAPI tools


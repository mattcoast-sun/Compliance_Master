# Complete Workflow API Endpoint

## Overview

The `/api/v1/workflow-complete` endpoint is a comprehensive, all-in-one API that executes the entire document compliance workflow in a single request. This endpoint combines all processing steps and includes file upload functionality.

## What It Does

This endpoint performs all four workflow steps automatically:

1. **Parse Document** - Extracts text and metadata from uploaded document (DOCX, PDF, etc.)
2. **Extract Fields** - Uses IBM Granite LLM to extract structured fields from the document
3. **Generate ISO Template** - Creates an ISO-compliant document template based on extracted fields
4. **Quality Check** - Validates the generated template against quality rules and ISO standards

## Endpoint Details

- **URL**: `/api/v1/workflow-complete`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Operation ID**: `workflowComplete`

## Request Parameters

### File Upload (Required)
- **Parameter**: `file`
- **Type**: File upload (multipart/form-data)
- **Description**: Document file to process (DOCX, PDF, etc.)

### Form Data (Optional)
- **iso_standard** (default: "ISO 9001:2015")
  - The ISO standard to follow for template generation
  - Example: "ISO 9001:2015", "ISO 13485:2016"

- **document_type** (default: "quality_system_record")
  - Type of ISO document to generate
  - Example: "quality_system_record", "procedure", "work_instruction"

## Response

The endpoint returns a comprehensive JSON response containing all workflow results:

```json
{
  "extracted_text": "Full extracted text from document...",
  "document_metadata": {
    "page_count": 5,
    "format": "docx",
    "...": "..."
  },
  "extracted_fields": {
    "document_title": "Device Calibration Procedure",
    "document_number": "QP-001",
    "revision_number": "3.0",
    "effective_date": "2024-01-15",
    "department": "Quality Assurance",
    "author": "John Smith",
    "purpose": "To establish procedures...",
    "scope": "This procedure applies to..."
  },
  "generated_template": "QUALITY SYSTEM RECORD\n\nTitle: Device Calibration Procedure...",
  "document_type": "quality_system_record",
  "iso_standard": "ISO 9001:2015",
  "quality_score": 85.5,
  "quality_grade": "B",
  "total_rules_checked": 12,
  "rules_passed": 10,
  "rules_failed": 2,
  "violations": [
    {
      "rule_id": "FIELD_001",
      "rule_name": "Department Field Present",
      "severity": "error",
      "description": "Checks if department field is present",
      "violation_details": "Department field found: Quality Assurance",
      "passed": true
    },
    ...
  ],
  "recommendations": [
    "Consider adding more detailed scope information",
    "Include references to related procedures"
  ],
  "source_document": "sample_device_calibration_procedure.docx",
  "timestamp": "2025-10-29T12:34:56.789Z",
  "success": true,
  "message": "Complete workflow executed successfully with quality grade B",
  "saved_file_path": "outputs/complete_workflow_quality_system_record_20251029_123456.json"
}
```

## Usage Examples

### Using cURL

```bash
curl -X POST "http://localhost:8765/api/v1/workflow-complete" \
  -F "file=@sample_device_calibration_procedure.docx" \
  -F "iso_standard=ISO 9001:2015" \
  -F "document_type=quality_system_record"
```

### Using Python (requests)

```python
import requests

url = "http://localhost:8765/api/v1/workflow-complete"

# Prepare the file
with open("sample_device_calibration_procedure.docx", "rb") as f:
    files = {
        "file": ("sample_device_calibration_procedure.docx", f, 
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    }
    
    # Optional parameters
    data = {
        "iso_standard": "ISO 9001:2015",
        "document_type": "quality_system_record"
    }
    
    # Make the request
    response = requests.post(url, files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Quality Score: {result['quality_score']}")
        print(f"Quality Grade: {result['quality_grade']}")
        print(f"Generated Template: {result['generated_template'][:200]}...")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
```

### Using JavaScript (Fetch API)

```javascript
async function processDocument() {
  const formData = new FormData();
  const fileInput = document.getElementById('fileInput');
  
  formData.append('file', fileInput.files[0]);
  formData.append('iso_standard', 'ISO 9001:2015');
  formData.append('document_type', 'quality_system_record');
  
  try {
    const response = await fetch('http://localhost:8765/api/v1/workflow-complete', {
      method: 'POST',
      body: formData
    });
    
    if (response.ok) {
      const result = await response.json();
      console.log('Quality Score:', result.quality_score);
      console.log('Quality Grade:', result.quality_grade);
      console.log('Generated Template:', result.generated_template);
    } else {
      console.error('Error:', response.status);
    }
  } catch (error) {
    console.error('Request failed:', error);
  }
}
```

### Using the Test Script

Run the provided test script:

```bash
# Make sure the API server is running
python main.py

# In another terminal, run the test script
python test_workflow_complete.py
```

## Comparison with Other Endpoints

### Individual Step Endpoints

If you need more control, you can use individual endpoints:

1. **Parse Document**: `POST /api/v1/parse-document`
2. **Extract Fields**: `POST /api/v1/extract-fields`
3. **Generate ISO Template**: `POST /api/v1/generate-iso-template`
4. **Check Quality**: `POST /api/v1/check-quality`

### Process Complete (without Quality Check)

The existing `POST /api/v1/process-complete` endpoint combines steps 1-3 but does **not** include the quality check. Use `/api/v1/workflow-complete` for the complete workflow including quality validation.

## Error Handling

The endpoint returns appropriate HTTP status codes:

- **200 OK**: Workflow completed successfully
- **400 Bad Request**: Invalid input (e.g., no file provided)
- **500 Internal Server Error**: Processing failed

Error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Performance Notes

- The complete workflow typically takes 30-60 seconds depending on:
  - Document size and complexity
  - LLM response time
  - Number of quality rules being checked
  
- For very large documents (>50 pages), consider breaking them into smaller sections

## Storage Options

Results can be saved locally or returned only in the API response:

- **Local Development**: Set `SAVE_LOCAL_COPIES=true` in `.env` to save results to `outputs/` directory
- **Production/Railway**: Leave `SAVE_LOCAL_COPIES=false` (default) for ephemeral storage

## Interactive API Documentation

Access the interactive Swagger UI documentation at:
- **Swagger UI**: http://localhost:8765/docs
- **ReDoc**: http://localhost:8765/redoc

These provide a web interface to test the endpoint directly from your browser.

## WatsonX Orchestrate Integration

This endpoint is fully compatible with IBM WatsonX Orchestrate:

1. The OpenAPI specification includes this endpoint
2. Operation ID: `workflowComplete`
3. Properly formatted request/response schemas
4. CORS enabled for cross-origin requests

## Support

For issues or questions:
1. Check the logs for detailed error messages
2. Review the OpenAPI specification at `/openapi.json`
3. Refer to the interactive documentation at `/docs`


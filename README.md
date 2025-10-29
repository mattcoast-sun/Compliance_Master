# Compliance Master API

An AI-powered document processing system that extracts information from documents and generates ISO-compliant templates using IBM Granite LLM and Docling.

## Features

- **Document Parsing**: Extract text from DOCX, PDF, and other document formats using Docling
- **AI Field Extraction**: Use IBM Granite LLM to intelligently extract structured information
- **ISO Template Generation**: Generate ISO-compliant document templates (e.g., quality system records)
- **Quality Validation**: Automated quality checks against ISO compliance rules
- **Complete Workflow**: All-in-one endpoint that executes all steps with a single file upload
- **WatsonX Orchestrate Compatible**: OpenAPI 3.0.3 specification with proper operation IDs
- **RESTful API**: FastAPI-based endpoints with automatic documentation

## Architecture

```
┌─────────────────┐
│  Upload DOCX    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Docling Parse  │ ───► Extract Text & Metadata
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ IBM Granite LLM │ ───► Extract Fields (AI)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ IBM Granite LLM │ ───► Generate ISO Template
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ IBM Granite LLM │ ───► Quality Check & Validation
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ISO Document +  │
│ Quality Report  │
└─────────────────┘
```

## Installation

### 1. Clone the repository

```bash
cd /Users/mattiasacosta/Documents/Programming_Projects/Compliance_Master
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the project root:

```env
# IBM WatsonX Configuration
WATSONX_API_KEY=your_watsonx_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# Model Configuration
GRANITE_MODEL_ID=ibm/granite-13b-chat-v2

# API Configuration
API_TITLE=Compliance Master API
API_VERSION=1.0.0
API_DESCRIPTION=AI-powered document processing and ISO template generation
```

## Usage

### Start the API server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8765
```

The API will be available at `http://localhost:8765`

### Access API Documentation

- **Swagger UI**: http://localhost:8765/docs
- **ReDoc**: http://localhost:8765/redoc
- **OpenAPI JSON**: http://localhost:8765/openapi.json

## API Endpoints

### 1. Health Check
```
GET /health
```
Check if the API is running and healthy.

### 2. Parse Document
```
POST /api/v1/parse-document
```
Upload a document (DOCX, PDF, etc.) and extract text content using Docling.

**Request**: Multipart form data with file
**Response**:
```json
{
  "extracted_text": "...",
  "metadata": {
    "filename": "document.docx",
    "num_pages": 5,
    "format": "docx"
  },
  "success": true,
  "message": "Document parsed successfully"
}
```

### 3. Extract Fields
```
POST /api/v1/extract-fields
```
Extract specific fields from document text using IBM Granite LLM.

**Request**:
```json
{
  "document_text": "...",
  "fields_to_extract": [
    "document_title",
    "document_number",
    "revision_number",
    "effective_date",
    "department",
    "author",
    "purpose",
    "scope"
  ]
}
```

**Response**:
```json
{
  "extracted_fields": [
    {
      "field_name": "document_title",
      "value": "Quality Management Procedure",
      "confidence": 0.95
    },
    ...
  ],
  "success": true,
  "message": "Fields extracted successfully"
}
```

### 4. Generate ISO Template
```
POST /api/v1/generate-iso-template
```
Generate an ISO-compliant document template using extracted fields.

**Request**:
```json
{
  "document_type": "quality_system_record",
  "extracted_fields": {
    "document_title": "Quality Management Procedure",
    "document_number": "QMP-001",
    "revision_number": "1.0",
    "effective_date": "2025-01-01",
    "department": "Quality Assurance",
    "author": "John Doe",
    "purpose": "To establish quality procedures",
    "scope": "All manufacturing processes"
  },
  "iso_standard": "ISO 9001:2015"
}
```

**Response**:
```json
{
  "generated_template": "...",
  "document_type": "quality_system_record",
  "iso_standard": "ISO 9001:2015",
  "success": true,
  "message": "ISO template generated successfully"
}
```

### 5. Check Quality
```
POST /api/v1/check-quality
```
Validate a generated ISO template against quality rules and ISO standards.

**Request**:
```json
{
  "generated_template": "...",
  "extracted_fields": { ... },
  "document_type": "quality_system_record",
  "iso_standard": "ISO 9001:2015"
}
```

**Response**:
```json
{
  "overall_score": 85.5,
  "quality_grade": "B",
  "total_rules_checked": 12,
  "rules_passed": 10,
  "rules_failed": 2,
  "violations": [ ... ],
  "recommendations": [ ... ],
  "success": true,
  "message": "Quality check completed with grade B"
}
```

### 6. Complete Processing Pipeline (Without Quality Check)
```
POST /api/v1/process-complete
```
Upload a document and complete the pipeline (parse, extract, generate) in one operation.

**Request**: Multipart form data with file and optional parameters
**Response**: Same as Generate ISO Template

### 7. Complete Workflow (All Steps + Quality Check) ⭐ NEW
```
POST /api/v1/workflow-complete
```
**The most comprehensive endpoint** - Upload a document and execute the complete workflow including quality validation in a single operation.

This endpoint performs all four steps automatically:
1. Parse document (extract text and metadata)
2. Extract fields using AI
3. Generate ISO-compliant template
4. Run quality checks and validation

**Request**: Multipart form data
- `file`: Document to process (DOCX, PDF, etc.) - **Required**
- `iso_standard`: ISO standard to follow (default: "ISO 9001:2015") - Optional
- `document_type`: Type of document (default: "quality_system_record") - Optional

**Example using cURL**:
```bash
curl -X POST "http://localhost:8765/api/v1/workflow-complete" \
  -F "file=@sample_document.docx" \
  -F "iso_standard=ISO 9001:2015" \
  -F "document_type=quality_system_record"
```

**Response**:
```json
{
  "extracted_text": "...",
  "document_metadata": { ... },
  "extracted_fields": { ... },
  "generated_template": "...",
  "document_type": "quality_system_record",
  "iso_standard": "ISO 9001:2015",
  "quality_score": 85.5,
  "quality_grade": "B",
  "total_rules_checked": 12,
  "rules_passed": 10,
  "rules_failed": 2,
  "violations": [ ... ],
  "recommendations": [ ... ],
  "source_document": "sample_document.docx",
  "timestamp": "2025-10-29T12:34:56.789Z",
  "success": true,
  "message": "Complete workflow executed successfully with quality grade B",
  "saved_file_path": "outputs/complete_workflow_quality_system_record_20251029_123456.json"
}
```

**Quick Test**:
```bash
# Using the provided test script
python test_workflow_complete.py

# Or using the shell script
./test_workflow_complete.sh
```

See [WORKFLOW_COMPLETE_API.md](WORKFLOW_COMPLETE_API.md) for detailed documentation and examples.

## WatsonX Orchestrate Integration

This API is designed to be compatible with WatsonX Orchestrate:

1. **OpenAPI 3.0.3 Specification**: The API uses OpenAPI 3.0.3 for compatibility
2. **Operation IDs**: Each endpoint has a unique `operation_id` for skill mapping
3. **Clear Descriptions**: Detailed summaries and descriptions for each endpoint
4. **Standardized Responses**: Consistent response models with proper schema definitions

### Importing into WatsonX Orchestrate

1. Access the OpenAPI specification: `http://localhost:8765/openapi.json`
2. Import the specification into WatsonX Orchestrate
3. Configure authentication with your API credentials
4. Map the skills to your automation workflows

## Project Structure

```
Compliance_Master/
├── main.py                 # FastAPI application and endpoints
├── config.py              # Configuration and settings
├── models.py              # Pydantic models for requests/responses
├── document_parser.py     # Docling document parsing service
├── llm_service.py         # IBM Granite LLM service
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Technologies Used

- **FastAPI**: Modern web framework for building APIs
- **Docling**: Document parsing and text extraction
- **IBM WatsonX AI**: Access to IBM Granite LLM models
- **Pydantic**: Data validation and settings management
- **Uvicorn**: ASGI server for running the application

## Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Invalid input or missing required fields
- **500 Internal Server Error**: Processing errors with detailed messages
- **Automatic cleanup**: Temporary files are automatically deleted after processing

## Logging

The application includes structured logging:
- Request/response logging
- Error tracking
- Service operation logs

Logs are output to console in the format:
```
TIMESTAMP - MODULE - LEVEL - MESSAGE
```

## Development

### Running tests
```bash
pytest
```

### Code formatting
```bash
black .
```

### Type checking
```bash
mypy .
```

## License

MIT License

## Support

For issues or questions, please contact the development team.


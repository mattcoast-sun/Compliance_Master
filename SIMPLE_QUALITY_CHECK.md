# Simple Quality Check Endpoint

## Overview

The **Simple Quality Check** endpoint is a brand new, ultra-simplified alternative to the complex quality check endpoint. It's designed to be **completely error-proof** and **guaranteed to work** by avoiding all complex typing and validation issues.

## Why This Endpoint?

The original quality check endpoint (`/api/v1/quality-check`) had complex typing requirements that could lead to validation errors like:
```
1 validation error for DynamicModel
extracted_fields
  Input should be a valid dictionary
```

This new endpoint **completely circumvents those issues** through radical simplicity.

## Endpoint Details

- **URL**: `/api/v1/quality-check-simple`
- **Method**: `POST`
- **Content-Type**: `application/json`

## Request Format

### Input (Super Simple!)
```json
{
  "generated_template": "Your generated ISO template text here..."
}
```

That's it! Just one field: `generated_template` (string).

### Response
```json
{
  "quality_report": "LLM-generated comprehensive quality report...",
  "success": true,
  "timestamp": "2024-10-30T12:34:56.789"
}
```

## How It Works

1. **Input**: You send only the generated ISO template as a single string
2. **LLM Analysis**: The LLM analyzes the template and generates a comprehensive quality report
3. **Output**: You receive a detailed quality assessment as plain text

### The LLM generates a report including:
- Overall Quality Score (0-100)
- Quality Grade (A, B, C, D, or F)
- Key Strengths
- Critical Issues Found
- Areas for Improvement
- Specific Recommendations
- ISO Compliance Status
- Formatting and Structure Assessment

## Usage Examples

### Python
```python
import requests

url = "http://localhost:8000/api/v1/quality-check-simple"

payload = {
    "generated_template": """
    ISO 9001:2015 Quality System Record
    
    Document Title: Calibration Procedure
    Document Number: QSR-2024-001
    ...
    """
}

response = requests.post(url, json=payload)
result = response.json()

print(result["quality_report"])
```

### cURL
```bash
curl -X POST http://localhost:8000/api/v1/quality-check-simple \
  -H "Content-Type: application/json" \
  -d '{
    "generated_template": "Your ISO template here..."
  }'
```

### JavaScript/Fetch
```javascript
const response = await fetch('http://localhost:8000/api/v1/quality-check-simple', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    generated_template: 'Your ISO template here...'
  })
});

const result = await response.json();
console.log(result.quality_report);
```

## Testing

Run the provided test script:
```bash
python test_simple_quality_check.py
```

## Integration with Workflow

You can easily integrate this with the ISO template generation endpoint:

```python
# Step 1: Generate ISO template
template_response = requests.post(
    "http://localhost:8000/api/v1/generate-iso-template",
    json={
        "document_type": "quality_system_record",
        "extracted_fields": {...},
        "iso_standard": "ISO 9001:2015"
    }
)

generated_template = template_response.json()["generated_template"]

# Step 2: Run simple quality check
quality_response = requests.post(
    "http://localhost:8000/api/v1/quality-check-simple",
    json={
        "generated_template": generated_template
    }
)

quality_report = quality_response.json()["quality_report"]
print(quality_report)
```

## Key Benefits

✅ **Zero Typing Errors**: Simple string in, string out
✅ **No Complex Validation**: No dictionaries, no nested objects, no type confusion
✅ **Guaranteed to Work**: If you can send a string, it will work
✅ **LLM-Powered**: Comprehensive AI-generated quality analysis
✅ **Easy to Integrate**: Works with any programming language or tool
✅ **Human-Readable Output**: Quality report in natural language

## Comparison with Original Endpoint

| Feature | Original `/quality-check` | New `/quality-check-simple` |
|---------|--------------------------|----------------------------|
| Input Complexity | High (template + fields + metadata) | Low (just template) |
| Typing Errors | Possible | Impossible |
| Structured Output | Yes (JSON with violations) | No (natural language) |
| LLM-Generated | Partially | Fully |
| Use Case | Programmatic processing | Human review |

## When to Use Which Endpoint

**Use `/quality-check-simple` when:**
- You want a quick quality assessment
- You're experiencing typing/validation errors
- You prefer human-readable reports
- You don't need structured violation data

**Use `/quality-check` when:**
- You need structured, parseable quality data
- You want specific rule violation details
- You're building automated quality pipelines
- You need the quality score for programmatic decisions

## Notes

- The endpoint requires the FastAPI server to be running
- The LLM must be configured and accessible via WatsonX
- Response time depends on template length and LLM performance
- The quality report format may vary based on LLM output

## Error Handling

The endpoint returns appropriate HTTP status codes:
- `200 OK`: Quality check completed successfully
- `400 Bad Request`: Empty or invalid template
- `500 Internal Server Error`: LLM or server error

Example error response:
```json
{
  "detail": "generated_template cannot be empty"
}
```


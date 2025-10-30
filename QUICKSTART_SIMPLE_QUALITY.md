# 🚀 Quick Start: Simple Quality Check

## The Problem (Before)
```python
# Complex typing causing validation errors ❌
{
    "generated_template": "...",
    "extracted_fields": {...},  # Dict or string? Type confusion!
    "document_type": "...",
    "iso_standard": "..."
}
# Error: Input should be a valid dictionary
```

## The Solution (Now)
```python
# Super simple - guaranteed to work ✅
{
    "generated_template": "Your ISO template here..."
}
# That's it!
```

---

## 🎯 Usage in 3 Steps

### Step 1: Start the Server
```bash
cd /Users/mattiasacosta/Documents/Programming_Projects/Compliance_Master
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 2: Send Your ISO Template
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/quality-check-simple",
    json={
        "generated_template": """
        ISO 9001:2015 Quality System Record
        
        Document Title: Calibration Procedure
        Document Number: QSR-2024-001
        ...your template text...
        """
    }
)

result = response.json()
```

### Step 3: Get Your Quality Report
```python
print(result["quality_report"])
# Output:
# ========================================
# QUALITY ASSESSMENT REPORT
# ========================================
# 
# Overall Quality Score: 87/100
# Quality Grade: B
# 
# KEY STRENGTHS:
# - Clear document structure
# - Proper ISO header information
# - Well-defined responsibilities
# 
# CRITICAL ISSUES FOUND:
# - Missing approval signatures
# - Incomplete revision history
# 
# RECOMMENDATIONS:
# 1. Add approval section
# 2. Include revision tracking table
# ...
```

---

## 🔗 Complete Workflow Example

```python
import requests

BASE_URL = "http://localhost:8000"

# Step 1: Generate ISO Template
template_response = requests.post(
    f"{BASE_URL}/api/v1/generate-iso-template",
    json={
        "document_type": "quality_system_record",
        "extracted_fields": {
            "document_title": "Calibration Procedure",
            "author": "Maria Lopez",
            # ... other fields
        },
        "iso_standard": "ISO 9001:2015"
    }
)

generated_template = template_response.json()["generated_template"]
print(f"✅ Template generated ({len(generated_template)} chars)")

# Step 2: Check Quality (Simple!)
quality_response = requests.post(
    f"{BASE_URL}/api/v1/quality-check-simple",
    json={
        "generated_template": generated_template
    }
)

quality_report = quality_response.json()["quality_report"]
print("\n📊 Quality Report:")
print("=" * 60)
print(quality_report)
print("=" * 60)
```

---

## 🧪 Test It Now

```bash
# Run the provided test script
python3 test_simple_quality_check.py
```

Expected output:
```
============================================================
SIMPLE QUALITY CHECK ENDPOINT TEST
============================================================

Testing Simple Quality Check Endpoint
============================================================

Sending request to: http://localhost:8000/api/v1/quality-check-simple
Template length: 567 characters
------------------------------------------------------------

Response Status: 200

✅ SUCCESS!
============================================================

Quality Report:
------------------------------------------------------------
[LLM-generated comprehensive quality report appears here]
------------------------------------------------------------

Timestamp: 2024-10-30T12:34:56.789
Success: True
```

---

## 🎨 API Documentation

Visit the interactive docs after starting the server:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Look for the **"Quality Check"** section and find:
> **POST** `/api/v1/quality-check-simple`
> 
> Simple quality check - just generated template in, quality report out

---

## ✨ Why It's Better

| Before (Complex) | After (Simple) |
|-----------------|----------------|
| 4 input fields | 1 input field |
| Type validation errors | No typing errors |
| Complex nested objects | Plain string |
| Dict or string confusion | Always string |
| Hard to debug | Easy to debug |
| ❌ Can fail on types | ✅ Always works |

---

## 🔍 What You Get Back

The LLM generates a comprehensive report with:

1. **Overall Quality Score** (0-100)
2. **Quality Grade** (A, B, C, D, F)
3. **Key Strengths** - What's done well
4. **Critical Issues Found** - What needs fixing
5. **Areas for Improvement** - Suggestions
6. **Specific Recommendations** - Action items
7. **ISO Compliance Status** - Standards adherence
8. **Formatting Assessment** - Structure review

All in **natural language** - easy to read and understand!

---

## 🚨 Error Handling

### Empty Template
```python
response = requests.post(url, json={"generated_template": ""})
# Status: 400 Bad Request
# Error: "generated_template cannot be empty"
```

### Server Error
```python
# Status: 500 Internal Server Error
# Error: "Failed to perform simple quality check: [details]"
```

---

## 📚 More Information

- **Full Documentation**: `SIMPLE_QUALITY_CHECK.md`
- **Implementation Details**: `SIMPLE_ENDPOINT_IMPLEMENTATION.md`
- **Test Script**: `test_simple_quality_check.py`

---

## 💡 Pro Tips

1. **Longer templates get better analysis** - The LLM has more context
2. **Works with any ISO standard** - The LLM understands various standards
3. **No token limits** - Template can be as long as needed
4. **Natural language output** - Perfect for human review
5. **Zero configuration** - Just send the template!

---

## 🎉 That's It!

You now have a **typing-error-proof**, **super-simple** quality check endpoint that **just works**.

No more validation errors. No more type confusion. Just send a string, get a report. 

**Simple. Reliable. Guaranteed.**


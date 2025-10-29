# Quick Setup Guide

## Prerequisites

- Python 3.8 or higher
- IBM Cloud account with WatsonX access
- pip (Python package manager)

## Step-by-Step Setup

### 1. Get IBM WatsonX Credentials

1. **Create an IBM Cloud account**: https://cloud.ibm.com/registration
2. **Access WatsonX**: Navigate to WatsonX.ai in your IBM Cloud dashboard
3. **Create a project**: Click "Create Project" in WatsonX
4. **Get your API Key**:
   - Go to https://cloud.ibm.com/iam/apikeys
   - Click "Create an IBM Cloud API key"
   - Copy and save the API key securely
5. **Get your Project ID**:
   - Open your WatsonX project
   - Click on "Manage" tab
   - Copy the Project ID

### 2. Install Dependencies

```bash
# Navigate to project directory
cd /Users/mattiasacosta/Documents/Programming_Projects/Compliance_Master

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy the template
cp env.template .env

# Edit .env file with your credentials
nano .env  # or use any text editor
```

Update the following values in `.env`:
- `WATSONX_API_KEY`: Your IBM Cloud API key
- `WATSONX_PROJECT_ID`: Your WatsonX project ID
- `WATSONX_URL`: Your region's WatsonX URL (default: US South)

### 4. Start the API Server

**Option 1: Using the run script**
```bash
./run.sh
```

**Option 2: Using uvicorn directly**
```bash
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8765
```

### 5. Access the API

Once the server is running, you can access:

- **API Documentation (Swagger)**: http://localhost:8765/docs
- **Alternative Documentation (ReDoc)**: http://localhost:8765/redoc
- **OpenAPI Specification**: http://localhost:8765/openapi.json
- **Health Check**: http://localhost:8765/health

### 6. Test the API

**Using the example script:**
```bash
python example_usage.py
```

**Using curl:**
```bash
# Health check
curl http://localhost:8765/health

# Parse a document
curl -X POST "http://localhost:8765/api/v1/parse-document" \
  -F "file=@path/to/your/document.docx"
```

**Using the Swagger UI:**
1. Navigate to http://localhost:8765/docs
2. Click on any endpoint to expand it
3. Click "Try it out"
4. Fill in the parameters
5. Click "Execute"

## Troubleshooting

### Error: "WATSONX_API_KEY not found"
- Make sure you created the `.env` file
- Verify the `.env` file contains your actual API key
- Check that the `.env` file is in the project root directory

### Error: "Module not found"
- Ensure your virtual environment is activated
- Run `pip install -r requirements.txt` again

### Error: Connection to WatsonX failed
- Verify your API key is correct
- Check your internet connection
- Ensure the WATSONX_URL matches your region

### Error: Project ID invalid
- Verify the project ID from your WatsonX project settings
- Ensure you're using a project that has LLM access enabled

## API Endpoints Overview

### 1. Parse Document
- **Endpoint**: `POST /api/v1/parse-document`
- **Purpose**: Extract text from DOCX, PDF, and other document formats
- **Input**: Document file (multipart/form-data)
- **Output**: Extracted text and metadata

### 2. Extract Fields
- **Endpoint**: `POST /api/v1/extract-fields`
- **Purpose**: Extract specific fields from document text using AI
- **Input**: Document text and list of fields to extract
- **Output**: Extracted fields with confidence scores

### 3. Generate ISO Template
- **Endpoint**: `POST /api/v1/generate-iso-template`
- **Purpose**: Generate ISO-compliant document template
- **Input**: Document type, extracted fields, ISO standard
- **Output**: Generated ISO document template

### 4. Complete Pipeline
- **Endpoint**: `POST /api/v1/process-complete`
- **Purpose**: End-to-end processing (parse + extract + generate)
- **Input**: Document file and optional parameters
- **Output**: Generated ISO document template

## WatsonX Orchestrate Integration

### Simplified OpenAPI Spec for Orchestrate

We've created a simplified OpenAPI 3.0.3 specification optimized for watsonx Orchestrate.

**File Location**: `openapi_orchestrate.json` (in project root)

This spec is specifically designed to:
- ✅ Work seamlessly with watsonx Orchestrate's file upload capabilities
- ✅ Use clear, simple schemas that Orchestrate can easily understand
- ✅ Include detailed descriptions for each endpoint and parameter
- ✅ Support multipart/form-data for file uploads

### Import API into WatsonX Orchestrate

**Step 1: Start Your API Server**
```bash
./run.sh
# Server will run on http://localhost:8765
```

**Step 2: Use the Simplified OpenAPI Spec**

The `openapi_orchestrate.json` file is ready to use. You can either:

**Option A: Use the pre-built spec (RECOMMENDED)**
```bash
# The file is already in your project root
ls -l openapi_orchestrate.json
```

**Option B: Generate from running API**
```bash
# Only if you want the auto-generated version
curl http://localhost:8765/openapi.json > compliance_master_openapi_auto.json
```

**Step 3: Import in WatsonX Orchestrate**

1. Log into **watsonx Orchestrate**: https://orchestrate.ibm.com
2. Navigate to **"Skills"** section
3. Click **"Add Skills"** or **"Import"**
4. Select **"Import OpenAPI"** or **"Custom API"**
5. Upload **`openapi_orchestrate.json`**
6. Review and confirm the imported skills

**Step 4: Configure Server URL**

- If deploying locally: Change server URL to your public URL (use ngrok or similar)
- If deploying to cloud: Update the `servers[0].url` in the OpenAPI spec to your deployed URL

Example using ngrok:
```bash
# In a new terminal, expose your local server
ngrok http 8765

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
# Update the OpenAPI spec or configure in Orchestrate
```

**Step 5: Configure Authentication (Optional)**

- If your API requires authentication, configure it in Orchestrate's skill settings
- Add any required headers or API keys
- For production, implement API key authentication in `main.py`

**Step 6: Test the Skills**

1. Use the skill tester in Orchestrate to verify each endpoint
2. Test file uploads with sample DOCX files
3. Create automation workflows using the skills

### File Upload in watsonx Orchestrate

✨ **File uploads work automatically!** Here's how:

#### How It Works

When you import the OpenAPI spec, Orchestrate automatically:
1. Detects file input parameters (`type: string, format: binary`)
2. Provides a file picker UI in the skill interface
3. Temporarily stores uploaded files
4. Sends them to your API as multipart/form-data

#### Using File Uploads in Orchestrate

**Method 1: Direct Upload**
- Users can drag and drop files directly in Orchestrate's chat interface
- Orchestrate handles the file and passes it to your API

**Method 2: From Connected Storage**
- Connect Box, Dropbox, Google Drive, or SharePoint
- Reference files stored in these systems
- Orchestrate retrieves and sends them to your API

**Method 3: Chained Workflows**
- Create multi-step workflows that pass files between skills
- Example: "Get file from Box" → "Parse Document" → "Generate ISO Template" → "Save to SharePoint"

#### Available File Operations (Skills)

1. **`parseDocument`** (operationId: `parseDocument`)
   - **Input**: Document file (DOCX, PDF, etc.)
   - **Output**: Extracted text and metadata
   - **Use Case**: Extract text from any document

2. **`processComplete`** (operationId: `processComplete`) ⭐ **RECOMMENDED**
   - **Input**: Document file + ISO standard + document type
   - **Output**: Complete ISO-compliant template
   - **Use Case**: One-step document processing
   - **Best For**: Most common use case - upload and get ISO template

3. **`extractFields`** (operationId: `extractFields`)
   - **Input**: Text content + list of fields
   - **Output**: Extracted field values with confidence scores
   - **Use Case**: Extract specific information from text

4. **`generateISOTemplate`** (operationId: `generateISOTemplate`)
   - **Input**: Extracted fields + ISO standard + document type
   - **Output**: ISO-compliant document template
   - **Use Case**: Generate template from already-extracted data

5. **`checkQuality`** (operationId: `checkQuality`)
   - **Input**: Generated template + extracted fields + document info
   - **Output**: Quality score, grade, violations, and recommendations
   - **Use Case**: Validate and check quality of generated templates

### Example Orchestrate Workflows

**Simple Workflow: Upload and Process**
```
User uploads DOCX file
  ↓
Call "processComplete" skill
  ↓
Receive ISO-compliant template
```

**Advanced Workflow: Multi-Step Processing**
```
Get file from Box/Dropbox
  ↓
Call "parseDocument" skill
  ↓
Call "extractFields" skill with specific fields
  ↓
Call "generateISOTemplate" skill
  ↓
Call "checkQuality" skill
  ↓
Save final template to SharePoint
  ↓
Send notification email
```

### Supported File Types

- **DOCX**: Microsoft Word documents ✅
- **PDF**: Portable Document Format ✅
- **Other**: Additional formats supported by Docling library

## Next Steps

1. **Test with your documents**: Upload sample DOCX files to test the parsing
2. **Customize field extraction**: Modify the `fields_to_extract` list in your requests
3. **Experiment with ISO standards**: Try different ISO standards (ISO 9001, ISO 27001, etc.)
4. **Integrate with your workflow**: Use the API in your applications or WatsonX Orchestrate

## Support

For issues or questions:
1. Check the logs in the console where the server is running
2. Review the API documentation at http://localhost:8765/docs
3. Examine the example usage script in `example_usage.py`
4. Check the README.md for detailed information

## Security Notes

- **Never commit your `.env` file** to version control
- Keep your IBM Cloud API key secure
- Use environment-specific credentials for different deployments
- Consider implementing authentication for production deployments

## Performance Tips

- For large documents, consider increasing the `MAX_NEW_TOKENS` parameter
- Use the individual endpoints for better control over the processing pipeline
- Cache extracted text to avoid re-parsing the same document
- Monitor your WatsonX usage and rate limits


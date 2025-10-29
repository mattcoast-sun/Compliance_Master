# watsonx Orchestrate Quick Start Guide

## 🚀 Getting Your API into Orchestrate (5 Minutes)

### What You Need
- ✅ `openapi_orchestrate.json` (already created in your project)
- ✅ Your API running locally or deployed
- ✅ watsonx Orchestrate account

### Step-by-Step

#### 1. Start Your API
```bash
cd /Users/mattiasacosta/Documents/Programming_Projects/Compliance_Master
./run.sh
```

Your API will be running at `http://localhost:8765`

#### 2. Make Your API Accessible to Orchestrate

**For Testing Locally:**
```bash
# Install ngrok (if you haven't already)
brew install ngrok

# Expose your local server
ngrok http 8765
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok-free.app`)

**For Production:**
Deploy your API to IBM Code Engine, Cloud Foundry, or any cloud platform.

#### 3. Update OpenAPI Spec with Your URL

Edit `openapi_orchestrate.json` and update the server URL:

```json
"servers": [
  {
    "url": "https://your-ngrok-url-or-deployed-url.com",
    "description": "Your API server"
  }
]
```

#### 4. Import into watsonx Orchestrate

1. Go to https://orchestrate.ibm.com
2. Click **"Skills"** in the left menu
3. Click **"Add Skills"** or **"+"** button
4. Select **"Import OpenAPI"**
5. Upload **`openapi_orchestrate.json`**
6. Review the imported skills (you should see 6 operations)
7. Click **"Import"** or **"Confirm"**

#### 5. Test Your Skills

1. In Orchestrate, go to the skill you just imported
2. Click **"Test"** or open the skill tester
3. Try the `processComplete` skill:
   - Upload a sample DOCX file
   - Set `iso_standard` to "ISO 9001:2015"
   - Set `document_type` to "quality_system_record"
   - Click **"Run"**
4. Review the generated ISO template!

---

## 📁 File Uploads in Orchestrate - YES, THEY WORK!

### How File Uploads Work

When you import the OpenAPI spec, Orchestrate **automatically detects** file parameters and provides:
- 📤 File picker UI
- ☁️ Temporary file storage
- 🔄 Automatic multipart/form-data handling

### Your File Upload Endpoints

#### 1. `parseDocument` (Parse Files Only)
```
Input:  Document file (DOCX, PDF)
Output: Extracted text + metadata
```

#### 2. `processComplete` ⭐ MOST USEFUL
```
Input:  Document file + ISO standard + document type
Output: Complete ISO-compliant template (one step!)
```

### Ways to Use Files in Orchestrate

#### Option 1: Direct Upload
Users upload files directly in the Orchestrate chat:
```
User: "Process this quality document"
Orchestrate: "Please upload the file"
User: [uploads calibration_procedure.docx]
Orchestrate: [runs processComplete skill]
Result: ISO-compliant template generated!
```

#### Option 2: From Cloud Storage
Connect Box, Dropbox, Google Drive, or SharePoint:
```
Orchestrate Workflow:
1. Get file from Box (file: "QA-Document.docx")
2. Run processComplete skill with that file
3. Save result to SharePoint
4. Send email notification
```

#### Option 3: Chained Skills
Build complex workflows:
```
Step 1: Get file from storage
Step 2: Parse document (parseDocument)
Step 3: Extract fields (extractFields)
Step 4: Generate template (generateISOTemplate)
Step 5: Check quality (checkQuality)
Step 6: Save to destination
```

---

## 🎯 Recommended Skills for Orchestrate Users

### For Beginners: Use `processComplete`
**One-step processing** - upload file and get ISO template immediately.

```json
{
  "operationId": "processComplete",
  "inputs": {
    "file": "your_document.docx",
    "iso_standard": "ISO 9001:2015",
    "document_type": "quality_system_record"
  }
}
```

### For Advanced Users: Chain Skills
Break down the process into steps for more control:

1. `parseDocument` → Get text from file
2. `extractFields` → Extract specific information
3. `generateISOTemplate` → Create compliant template
4. `checkQuality` → Validate the output

---

## 🔧 Troubleshooting

### "Cannot connect to server"
- ✅ Make sure your API is running (`./run.sh`)
- ✅ Check your ngrok URL is still active (they expire after 2 hours on free tier)
- ✅ Verify the server URL in `openapi_orchestrate.json` matches your deployment

### "File upload failed"
- ✅ Check file format (DOCX and PDF work best)
- ✅ Ensure file size is under 10MB
- ✅ Verify the API endpoint is correctly defined with `multipart/form-data`

### "Skill not found" or "Operation failed"
- ✅ Re-import the OpenAPI spec
- ✅ Check that all required parameters are provided
- ✅ Look at the API logs for error messages

---

## 📝 Quick Testing with curl

Before importing to Orchestrate, test locally:

```bash
# Health check
curl http://localhost:8765/health

# Parse a document
curl -X POST "http://localhost:8765/api/v1/parse-document" \
  -F "file=@sample_device_calibration_procedure.docx"

# Complete pipeline (recommended)
curl -X POST "http://localhost:8765/api/v1/process-complete" \
  -F "file=@sample_device_calibration_procedure.docx" \
  -F "iso_standard=ISO 9001:2015" \
  -F "document_type=quality_system_record"
```

---

## 🎉 You're Ready!

Your Compliance Master API is now ready for watsonx Orchestrate with full file upload support!

### Key Files
- ✅ `openapi_orchestrate.json` - OpenAPI 3.0.3 spec (import this)
- ✅ `main.py` - Your FastAPI application
- ✅ `SETUP.md` - Detailed setup instructions
- ✅ This file - Quick reference guide

### Next Steps
1. Import the OpenAPI spec into Orchestrate
2. Test the `processComplete` skill with a sample file
3. Build automation workflows
4. Share with your team!

---

## 💡 Pro Tips

1. **Start with `processComplete`** - It's the easiest and most useful skill
2. **Use ngrok for testing** - Free and quick to set up
3. **Test locally first** - Use curl or the Swagger UI at http://localhost:8765/docs
4. **Check the logs** - Run `./run.sh` and watch the console for errors
5. **Save your ngrok URL** - You'll need to update it when it expires

---

Need help? Check `SETUP.md` for detailed instructions!


# Setting Up Compliance Master from GitHub

This guide is for anyone cloning this repository from GitHub.

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/mattcoast-sun/Compliance_Master.git
cd Compliance_Master
```

### 2. Set Up Environment Variables

The repository includes a template file for environment variables:

```bash
# Copy the template
cp env.template .env

# Edit with your credentials
nano .env  # or use any text editor
```

**Required Variables:**
- `WATSONX_API_KEY` - Your IBM Cloud API key
- `WATSONX_PROJECT_ID` - Your WatsonX project ID
- `WATSONX_URL` - Your region's WatsonX URL (default: US South)

**How to Get Credentials:**
1. Create an IBM Cloud account: https://cloud.ibm.com/registration
2. Access WatsonX.ai in your IBM Cloud dashboard
3. Create a project
4. Get your API key: https://cloud.ibm.com/iam/apikeys
5. Get your Project ID from the project settings

### 3. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate    # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 4. Run the Server

```bash
# Make the run script executable (macOS/Linux)
chmod +x run.sh

# Start the server
./run.sh
```

Or manually:
```bash
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8765
```

### 5. Test the API

Visit http://localhost:8765/docs to see the interactive API documentation.

## Important Security Notes

⚠️ **NEVER commit your `.env` file to Git!**

The `.gitignore` file is configured to exclude:
- `.env` (your API keys and secrets)
- `venv/` (virtual environment)
- `__pycache__/` (Python cache)
- `outputs/` and `quality_checks/` (generated files)

## watsonx Orchestrate Integration

To use this API with watsonx Orchestrate:

1. Start your API server (see above)
2. Follow the instructions in `ORCHESTRATE_QUICKSTART.md`
3. Import the `openapi_orchestrate.json` spec into Orchestrate

## Documentation

- **Quick Setup**: `SETUP.md`
- **Orchestrate Guide**: `ORCHESTRATE_QUICKSTART.md`
- **API Documentation**: `README.md`
- **Deployment**: `DEPLOYMENT.md`

## Example Usage

```bash
# Test health check
curl http://localhost:8765/health

# Parse a document
curl -X POST "http://localhost:8765/api/v1/parse-document" \
  -F "file=@your_document.docx"

# Complete pipeline
curl -X POST "http://localhost:8765/api/v1/process-complete" \
  -F "file=@your_document.docx" \
  -F "iso_standard=ISO 9001:2015" \
  -F "document_type=quality_system_record"
```

Or use the Python example:
```bash
python example_usage.py
```

## Need Help?

Check the detailed documentation:
- `SETUP.md` - Comprehensive setup guide
- `README.md` - Project overview and API details
- `ORCHESTRATE_QUICKSTART.md` - watsonx Orchestrate integration

## Contributing

When contributing, please:
1. Never commit `.env` files or API keys
2. Test your changes locally before pushing
3. Update documentation if you add new features
4. Follow the existing code style

## License

See LICENSE file for details.


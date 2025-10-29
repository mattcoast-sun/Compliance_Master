"""
FastAPI application for Compliance Master
WatsonX Orchestrate compatible API with OpenAPI 3.0.3 specification
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import logging
import json
from datetime import datetime
from pathlib import Path

from config import settings
from models import (
    DocumentParseResponse,
    FieldExtractionRequest,
    FieldExtractionResponse,
    ExtractedField,
    ISOTemplateRequest,
    ISOTemplateResponse,
    HealthCheckResponse,
    QualityCheckRequest,
    QualityCheckResponse,
    RuleViolation
)
from document_parser import DocumentParser
from llm_service import GraniteLLMService
from quality_rules import QUALITY_RULES, format_rules_for_prompt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app with OpenAPI 3.0.3
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    openapi_version="3.0.3",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS for WatsonX Orchestrate compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
document_parser = DocumentParser()
llm_service = GraniteLLMService()

# Storage configuration
# Set SAVE_LOCAL_COPIES=true in .env for local development
# On Railway/production, leave it false (ephemeral filesystem)
SAVE_LOCAL_COPIES = os.getenv("SAVE_LOCAL_COPIES", "false").lower() == "true"

# Create outputs directory only if saving locally
if SAVE_LOCAL_COPIES:
    OUTPUTS_DIR = Path("outputs")
    OUTPUTS_DIR.mkdir(exist_ok=True)
    QUALITY_CHECKS_DIR = Path("quality_checks")
    QUALITY_CHECKS_DIR.mkdir(exist_ok=True)
    logger.info("Local file saving enabled - outputs will be saved to disk")
else:
    logger.info("Local file saving disabled - outputs returned in JSON only (production mode)")


def save_output_json(data: dict, prefix: str = "output") -> str:
    """
    Save output data as JSON file with timestamp.
    Only saves if SAVE_LOCAL_COPIES is enabled.
    
    Args:
        data: Dictionary data to save
        prefix: Filename prefix
        
    Returns:
        Path to saved file or None if saving disabled
    """
    if not SAVE_LOCAL_COPIES:
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.json"
    filepath = OUTPUTS_DIR / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved output to: {filepath}")
    return str(filepath)


@app.get(
    "/health",
    response_model=HealthCheckResponse,
    tags=["System"],
    summary="Health check endpoint",
    description="Check if the API is running and healthy"
)
async def health_check():
    """Health check endpoint"""
    return HealthCheckResponse(
        status="healthy",
        version=settings.api_version
    )


@app.post(
    "/api/v1/parse-document",
    response_model=DocumentParseResponse,
    tags=["Document Processing"],
    summary="Parse document and extract text",
    description="Upload a document (DOCX, PDF, etc.) and extract its text content using Docling",
    operation_id="parseDocument"
)
async def parse_document(
    file: UploadFile = File(..., description="Document file to parse (DOCX, PDF, etc.)")
):
    """
    Parse a document and extract text content.
    
    This endpoint accepts various document formats (DOCX, PDF, etc.) and uses
    Docling to extract the text content and metadata.
    """
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    # Create temporary file
    temp_file = None
    try:
        # Save uploaded file to temporary location
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Parse document
        extracted_text, metadata = document_parser.parse_document(temp_file_path)
        
        return DocumentParseResponse(
            extracted_text=extracted_text,
            metadata=metadata,
            success=True,
            message="Document parsed successfully"
        )
        
    except Exception as e:
        logger.error(f"Error parsing document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse document: {str(e)}"
        )
    
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file: {str(e)}")


@app.post(
    "/api/v1/extract-fields",
    response_model=FieldExtractionResponse,
    tags=["Field Extraction"],
    summary="Extract fields from document text",
    description="Use IBM Granite LLM to extract specific fields from document text",
    operation_id="extractFields"
)
async def extract_fields(request: FieldExtractionRequest):
    """
    Extract specific fields from document text using AI.
    
    This endpoint uses IBM Granite LLM via WatsonX to intelligently extract
    structured information from unstructured document text.
    """
    try:
        # Validate input
        if not request.document_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document text cannot be empty"
            )
        
        # Extract fields using LLM
        extracted_fields_data = llm_service.extract_fields(
            document_text=request.document_text,
            fields_to_extract=request.fields_to_extract
        )
        
        # Convert to response model
        extracted_fields = [
            ExtractedField(**field_data)
            for field_data in extracted_fields_data
        ]
        
        return FieldExtractionResponse(
            extracted_fields=extracted_fields,
            success=True,
            message="Fields extracted successfully"
        )
        
    except Exception as e:
        logger.error(f"Error extracting fields: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract fields: {str(e)}"
        )


@app.post(
    "/api/v1/generate-iso-template",
    response_model=ISOTemplateResponse,
    tags=["ISO Template Generation"],
    summary="Generate ISO document template",
    description="Generate an ISO-compliant document template using extracted fields and IBM Granite LLM",
    operation_id="generateISOTemplate"
)
async def generate_iso_template(request: ISOTemplateRequest):
    """
    Generate an ISO-compliant document template.
    
    This endpoint uses IBM Granite LLM to generate a complete ISO document
    template (e.g., quality system record) based on extracted fields and
    specified ISO standard requirements.
    """
    try:
        # Validate input
        if not request.extracted_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Extracted fields cannot be empty"
            )
        
        # Generate template using LLM
        generated_template = llm_service.generate_iso_template(
            document_type=request.document_type,
            extracted_fields=request.extracted_fields,
            iso_standard=request.iso_standard
        )
        
        # Prepare response data
        response_data = {
            "generated_template": generated_template,
            "document_type": request.document_type,
            "iso_standard": request.iso_standard,
            "extracted_fields": request.extracted_fields,
            "timestamp": datetime.now().isoformat(),
            "success": True,
            "message": "ISO template generated successfully"
        }
        
        # Save to JSON file
        saved_path = save_output_json(response_data, prefix=f"iso_template_{request.document_type}")
        
        return ISOTemplateResponse(
            generated_template=generated_template,
            document_type=request.document_type,
            iso_standard=request.iso_standard,
            success=True,
            message="ISO template generated successfully",
            saved_file_path=saved_path
        )
        
    except Exception as e:
        logger.error(f"Error generating ISO template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate ISO template: {str(e)}"
        )


@app.post(
    "/api/v1/process-complete",
    response_model=ISOTemplateResponse,
    tags=["Complete Processing"],
    summary="Complete document processing pipeline",
    description="Upload a document, extract fields, and generate ISO template in one operation",
    operation_id="processComplete"
)
async def process_complete(
    file: UploadFile = File(..., description="Document file to process"),
    iso_standard: str = "ISO 9001:2015",
    document_type: str = "quality_system_record"
):
    """
    Complete document processing pipeline.
    
    This endpoint combines all operations:
    1. Parse the uploaded document
    2. Extract relevant fields using AI
    3. Generate an ISO-compliant template
    
    This is a convenience endpoint for end-to-end processing.
    """
    temp_file = None
    try:
        # Step 1: Parse document
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        extracted_text, metadata = document_parser.parse_document(temp_file_path)
        
        # Step 2: Extract fields
        default_fields = [
            "document_title",
            "document_number",
            "revision_number",
            "effective_date",
            "department",
            "author",
            "purpose",
            "scope"
        ]
        
        extracted_fields_data = llm_service.extract_fields(
            document_text=extracted_text,
            fields_to_extract=default_fields
        )
        
        # Convert to dictionary
        fields_dict = {
            field["field_name"]: field["value"]
            for field in extracted_fields_data
        }
        
        # Step 3: Generate ISO template
        generated_template = llm_service.generate_iso_template(
            document_type=document_type,
            extracted_fields=fields_dict,
            iso_standard=iso_standard
        )
        
        # Prepare response data
        response_data = {
            "generated_template": generated_template,
            "document_type": document_type,
            "iso_standard": iso_standard,
            "extracted_fields": fields_dict,
            "source_document": file.filename,
            "document_metadata": metadata,
            "timestamp": datetime.now().isoformat(),
            "success": True,
            "message": "Complete processing pipeline executed successfully"
        }
        
        # Save to JSON file
        saved_path = save_output_json(response_data, prefix=f"complete_pipeline_{document_type}")
        
        return ISOTemplateResponse(
            generated_template=generated_template,
            document_type=document_type,
            iso_standard=iso_standard,
            success=True,
            message="Complete processing pipeline executed successfully",
            saved_file_path=saved_path
        )
        
    except Exception as e:
        logger.error(f"Error in complete processing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete processing: {str(e)}"
        )
    
    finally:
        if temp_file and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file: {str(e)}")


@app.post(
    "/api/v1/check-quality",
    response_model=QualityCheckResponse,
    tags=["Quality Assurance"],
    summary="Check quality of generated ISO template",
    description="Validate a generated ISO template against quality rules using AI",
    operation_id="checkQuality"
)
async def check_quality(request: QualityCheckRequest):
    """
    Check the quality of a generated ISO template against defined quality rules.
    
    This endpoint uses IBM Granite LLM to validate the generated template
    against a comprehensive set of quality rules, checking for:
    - Missing or invalid fields (e.g., Department not found)
    - Date validity (e.g., dates older than 2 years)
    - Content completeness and structure
    - ISO compliance requirements
    """
    try:
        # Validate input
        if not request.generated_template.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Generated template cannot be empty"
            )
        
        # Format quality rules for the LLM
        rules_text = format_rules_for_prompt()
        
        # Run quality check using LLM
        quality_results = llm_service.check_quality(
            generated_template=request.generated_template,
            extracted_fields=request.extracted_fields,
            document_type=request.document_type,
            iso_standard=request.iso_standard,
            quality_rules=rules_text
        )
        
        # Process violations
        violations = []
        rules_passed = 0
        rules_failed = 0
        
        for violation_data in quality_results.get("violations", []):
            violation = RuleViolation(**violation_data)
            violations.append(violation)
            if violation.passed:
                rules_passed += 1
            else:
                rules_failed += 1
        
        total_rules_checked = len(violations)
        
        # Calculate overall score (weighted by severity)
        if total_rules_checked > 0:
            severity_weights = {"error": 10, "warning": 5, "info": 2}
            max_score = sum(
                severity_weights.get(v.severity, 1) 
                for v in violations
            )
            actual_score = sum(
                severity_weights.get(v.severity, 1) 
                for v in violations if v.passed
            )
            overall_score = (actual_score / max_score * 100) if max_score > 0 else 0
        else:
            overall_score = 100.0
        
        # Determine quality grade
        if overall_score >= 90:
            quality_grade = "A"
        elif overall_score >= 80:
            quality_grade = "B"
        elif overall_score >= 70:
            quality_grade = "C"
        elif overall_score >= 60:
            quality_grade = "D"
        else:
            quality_grade = "F"
        
        # Prepare response data for saving
        response_data = {
            "overall_score": overall_score,
            "quality_grade": quality_grade,
            "total_rules_checked": total_rules_checked,
            "rules_passed": rules_passed,
            "rules_failed": rules_failed,
            "violations": [
                {
                    "rule_id": v.rule_id,
                    "rule_name": v.rule_name,
                    "severity": v.severity,
                    "description": v.description,
                    "violation_details": v.violation_details,
                    "passed": v.passed
                }
                for v in violations
            ],
            "recommendations": quality_results.get("recommendations", []),
            "document_info": {
                "document_type": request.document_type,
                "iso_standard": request.iso_standard,
                "extracted_fields": request.extracted_fields
            },
            "timestamp": datetime.now().isoformat(),
            "success": True,
            "message": f"Quality check completed with grade {quality_grade}"
        }
        
        # Save to quality checks directory (only if local saving enabled)
        filepath = None
        if SAVE_LOCAL_COPIES:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"quality_check_{request.document_type}_{timestamp}.json"
            filepath = QUALITY_CHECKS_DIR / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(response_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved quality check report to: {filepath}")
            filepath = str(filepath)
        
        return QualityCheckResponse(
            overall_score=overall_score,
            total_rules_checked=total_rules_checked,
            rules_passed=rules_passed,
            rules_failed=rules_failed,
            violations=violations,
            recommendations=quality_results.get("recommendations", []),
            quality_grade=quality_grade,
            success=True,
            message=f"Quality check completed with grade {quality_grade}",
            saved_file_path=filepath  # None if SAVE_LOCAL_COPIES=false
        )
        
    except Exception as e:
        logger.error(f"Error checking quality: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check quality: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765)


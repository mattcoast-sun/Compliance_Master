"""
Pydantic models for request and response schemas
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any


class DocumentParseRequest(BaseModel):
    """Request model for document parsing"""
    pass


class PreloadedDocumentRequest(BaseModel):
    """Request model for processing pre-loaded sample documents"""
    document_id: str = Field(
        ..., 
        description="ID of the pre-loaded document to process (e.g., 'sample_calibration', 'non_compliant_iso')"
    )
    iso_standard: str = Field(
        default="ISO 9001:2015", 
        description="ISO standard to follow"
    )
    document_type: str = Field(
        default="quality_system_record", 
        description="Type of ISO document to generate"
    )


class DocumentParseResponse(BaseModel):
    """Response model for document parsing"""
    extracted_text: str = Field(..., description="Extracted text from the document")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    success: bool = Field(..., description="Whether the parsing was successful")
    message: Optional[str] = Field(None, description="Additional information or error message")


class FieldExtractionRequest(BaseModel):
    """Request model for field extraction"""
    document_text: str = Field(..., description="The text content to extract fields from")
    fields_to_extract: List[str] = Field(
        default_factory=lambda: [
            "document_title",
            "document_number",
            "revision_number",
            "effective_date",
            "department",
            "author",
            "purpose",
            "scope"
        ],
        description="List of fields to extract from the document"
    )


class ExtractedField(BaseModel):
    """Model for an extracted field"""
    field_name: str = Field(..., description="Name of the extracted field")
    value: Optional[str] = Field(None, description="Extracted value")
    confidence: Optional[float] = Field(None, description="Confidence score (0-1)")


class FieldExtractionResponse(BaseModel):
    """Response model for field extraction"""
    extracted_fields: List[ExtractedField] = Field(..., description="List of extracted fields")
    success: bool = Field(..., description="Whether the extraction was successful")
    message: Optional[str] = Field(None, description="Additional information or error message")


class ISOTemplateRequest(BaseModel):
    """Request model for ISO template generation"""
    document_type: str = Field(
        default="quality_system_record",
        description="Type of ISO document to generate"
    )
    extracted_fields: Dict[str, str] = Field(
        ...,
        description="Dictionary of extracted fields to populate in the template"
    )
    iso_standard: str = Field(
        default="ISO 9001:2015",
        description="ISO standard to follow"
    )


class ISOTemplateResponse(BaseModel):
    """Response model for ISO template generation"""
    generated_template: str = Field(..., description="The generated ISO document template")
    document_type: str = Field(..., description="Type of document generated")
    iso_standard: str = Field(..., description="ISO standard followed")
    success: bool = Field(..., description="Whether the generation was successful")
    message: Optional[str] = Field(None, description="Additional information or error message")
    saved_file_path: Optional[str] = Field(None, description="Path to the saved JSON output file")


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")


class QualityCheckRequest(BaseModel):
    """Request model for quality check"""
    generated_template: str = Field(..., description="The generated ISO template to check")
    extracted_fields: Dict[str, str] = Field(default_factory=dict, description="The extracted fields used to generate the template")
    document_type: str = Field(..., description="Type of document")
    iso_standard: str = Field(..., description="ISO standard")


class RuleViolation(BaseModel):
    """Model for a quality rule violation"""
    rule_id: str = Field(..., description="Unique identifier for the rule")
    rule_name: str = Field(..., description="Name of the rule")
    severity: str = Field(..., description="Severity level: error, warning, info")
    description: str = Field(..., description="Description of what was checked")
    violation_details: str = Field(..., description="Details of the violation found")
    passed: bool = Field(..., description="Whether the rule passed")


class QualityCheckResponse(BaseModel):
    """Response model for quality check"""
    overall_score: float = Field(..., description="Overall quality score (0-100)")
    total_rules_checked: int = Field(..., description="Total number of rules checked")
    rules_passed: int = Field(..., description="Number of rules passed")
    rules_failed: int = Field(..., description="Number of rules failed")
    violations: List[RuleViolation] = Field(..., description="List of rule violations")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for improvement")
    quality_grade: str = Field(..., description="Quality grade: A, B, C, D, F")
    success: bool = Field(..., description="Whether the quality check was successful")
    message: Optional[str] = Field(None, description="Additional information")
    saved_file_path: Optional[str] = Field(None, description="Path to the saved quality check report")


class CompleteWorkflowResponse(BaseModel):
    """Response model for complete workflow with all steps"""
    # Document parsing results
    extracted_text: str = Field(..., description="Extracted text from the document")
    document_metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    
    # Field extraction results
    extracted_fields: Dict[str, str] = Field(..., description="Dictionary of extracted fields")
    
    # ISO template generation results
    generated_template: str = Field(..., description="The generated ISO document template")
    document_type: str = Field(..., description="Type of document generated")
    iso_standard: str = Field(..., description="ISO standard followed")
    
    # Quality check results
    quality_score: float = Field(..., description="Overall quality score (0-100)")
    quality_grade: str = Field(..., description="Quality grade: A, B, C, D, F")
    total_rules_checked: int = Field(..., description="Total number of rules checked")
    rules_passed: int = Field(..., description="Number of rules passed")
    rules_failed: int = Field(..., description="Number of rules failed")
    violations: List[RuleViolation] = Field(..., description="List of rule violations")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for improvement")
    
    # General response fields
    source_document: str = Field(..., description="Original document filename")
    timestamp: str = Field(..., description="Timestamp of processing")
    success: bool = Field(..., description="Whether the entire workflow was successful")
    message: str = Field(..., description="Status message")
    saved_file_path: Optional[str] = Field(None, description="Path to the saved output file")


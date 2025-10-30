"""
LLM service using IBM Granite models via WatsonX
"""
from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from typing import List, Dict, Any
from datetime import datetime
import json
import re
import logging
from config import settings

logger = logging.getLogger(__name__)


class GraniteLLMService:
    """Service for interacting with IBM Granite LLM via WatsonX"""
    
    def __init__(self):
        """Initialize the Granite LLM service"""
        self.credentials = {
            "url": settings.watsonx_url,
            "apikey": settings.watsonx_api_key
        }
        self.project_id = settings.watsonx_project_id
        self.model_id = settings.granite_model_id
        
        # Model parameters
        self.parameters = {
            GenParams.DECODING_METHOD: "greedy",
            GenParams.MAX_NEW_TOKENS: 2000,
            GenParams.MIN_NEW_TOKENS: 1,
            GenParams.TEMPERATURE: 0.1,
            GenParams.TOP_K: 50,
            GenParams.TOP_P: 1
        }
    
    def _get_model(self) -> Model:
        """Get or create model instance"""
        return Model(
            model_id=self.model_id,
            params=self.parameters,
            credentials=self.credentials,
            project_id=self.project_id
        )
    
    def extract_fields(self, document_text: str, fields_to_extract: List[str]) -> List[Dict[str, Any]]:
        """
        Extract specific fields from document text using LLM
        
        Args:
            document_text: The text content to analyze
            fields_to_extract: List of field names to extract
            
        Returns:
            List of dictionaries containing field_name, value, and confidence
        """
        try:
            # Create prompt for field extraction
            fields_list = "\n".join([f"- {field}" for field in fields_to_extract])
            
            prompt = f"""You are an expert at extracting structured information from documents.

Given the following document text, extract the requested fields. If a field is not found in the document, indicate "Not found".

Document text:
{document_text[:3000]}

Extract the following fields:
{fields_list}

Provide your response as a JSON object with this exact format:
{{
  "field_name": {{
    "value": "extracted value or 'Not found'",
    "confidence": 0.95
  }}
}}

Response:"""

            model = self._get_model()
            response = model.generate_text(prompt=prompt)
            
            # Parse the response
            try:
                # Try to extract JSON from response
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    parsed_data = json.loads(json_str)
                else:
                    parsed_data = json.loads(response)
                
                # Convert to list format
                extracted_fields = []
                for field_name in fields_to_extract:
                    field_data = parsed_data.get(field_name, {})
                    if isinstance(field_data, dict):
                        extracted_fields.append({
                            "field_name": field_name,
                            "value": field_data.get("value", "Not found"),
                            "confidence": field_data.get("confidence", 0.5)
                        })
                    else:
                        # Handle case where LLM returned direct value
                        extracted_fields.append({
                            "field_name": field_name,
                            "value": str(field_data) if field_data else "Not found",
                            "confidence": 0.7
                        })
                
                return extracted_fields
                
            except json.JSONDecodeError:
                logger.error(f"Failed to parse LLM response as JSON: {response}")
                # Return default structure
                return [
                    {
                        "field_name": field,
                        "value": "Error: Could not extract",
                        "confidence": 0.0
                    }
                    for field in fields_to_extract
                ]
                
        except Exception as e:
            logger.error(f"Error in field extraction: {str(e)}")
            raise
    
    def generate_iso_template(
        self,
        document_type: str,
        extracted_fields: Dict[str, str],
        iso_standard: str
    ) -> str:
        """
        Generate an ISO document template using extracted fields
        
        Args:
            document_type: Type of ISO document to generate
            extracted_fields: Dictionary of extracted fields (can be None or empty dict)
            iso_standard: ISO standard to follow
            
        Returns:
            Generated ISO document template as string
        """
        try:
            # Handle None or empty extracted_fields
            if extracted_fields is None:
                extracted_fields = {}
            
            # Prepare fields for prompt
            if len(extracted_fields) > 0:
                fields_text = "\n".join([f"- {key}: {value}" for key, value in extracted_fields.items()])
            else:
                fields_text = "(No fields provided - template will use generic placeholders)"
            
            prompt = f"""You are an expert in creating ISO compliant documentation.

Generate a complete {document_type} template following the {iso_standard} standard.

Use the following extracted information to populate the template:
{fields_text}

The template should include:
1. Document header with document number, revision, date
2. Purpose and scope section
3. Definitions and references
4. Procedure or record structure appropriate for {document_type}
5. Responsibilities section
6. Related documents section
7. Revision history section

Create a professional, well-formatted document template that complies with {iso_standard} requirements.

Template:"""

            model = self._get_model()
            response = model.generate_text(prompt=prompt)
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating ISO template: {str(e)}")
            raise
    
    def verify_and_sanitize_inputs(
        self,
        generated_template: str,
        extracted_fields: dict,
        document_type: str,
        iso_standard: str
    ) -> dict:
        """
        Use LLM to verify and sanitize inputs for quality check.
        
        This acts as a smart filter after rules-based deserialization to catch
        edge cases, malformed data, or unexpected formats that simple parsing missed.
        
        Args:
            generated_template: The template text (may still contain artifacts)
            extracted_fields: Dictionary of fields (may be incomplete or malformed)
            document_type: Type of document
            iso_standard: ISO standard
            
        Returns:
            Dictionary containing:
            - verified_template: Clean, verified template text
            - verified_fields: Clean, verified extracted fields
            - issues_found: List of issues detected and fixed
            - confidence: Confidence score (0-1) that inputs are valid
        """
        try:
            # Prepare extracted_fields summary for prompt
            if extracted_fields and len(extracted_fields) > 0:
                fields_summary = "\n".join([
                    f"  - {key}: {value[:100]}..." if len(str(value)) > 100 else f"  - {key}: {value}"
                    for key, value in extracted_fields.items()
                ])
            else:
                fields_summary = "  (No fields provided)"
            
            prompt = f"""You are a data validation expert. Your task is to verify and sanitize inputs for a quality check system.

CONTEXT:
- Document Type: {document_type}
- ISO Standard: {iso_standard}

INPUT DATA TO VERIFY:

1. GENERATED TEMPLATE (first 1000 chars):
{generated_template[:1000]}

2. EXTRACTED FIELDS:
{fields_summary}

YOUR TASK:
Analyze these inputs and determine:

1. Is the generated_template valid text, or does it contain:
   - Nested JSON structures that should be extracted?
   - Escaped characters (\\n, \\", etc.) that should be unescaped?
   - Serialization artifacts or encoding issues?
   - Multiple nested layers of the same data?

2. Are the extracted_fields valid, or do they contain:
   - String values that should be "Not found" or "N/A"?
   - Unusual formatting or encoding issues?
   - Duplicate or nested data?

3. Overall confidence: How confident are you (0.0 to 1.0) that these inputs are clean and ready for processing?

RESPOND IN JSON FORMAT:
{{
  "template_issues": [
    "Issue 1: Description of what's wrong with the template",
    "Issue 2: Another issue found"
  ],
  "template_needs_cleaning": true,
  "cleaned_template_instructions": "If cleaning needed, describe what to extract/fix",
  
  "fields_issues": [
    "Issue 1: Description of what's wrong with fields",
    "Issue 2: Another issue"
  ],
  "fields_need_cleaning": false,
  "cleaned_fields_suggestions": {{}},
  
  "confidence": 0.85,
  "recommendation": "PROCEED | CLEAN_TEMPLATE | CLEAN_FIELDS | CLEAN_BOTH | REJECT",
  "summary": "Brief summary of the verification"
}}

Return ONLY the JSON object."""

            model = self._get_model()
            response = model.generate_text(prompt=prompt)
            
            # Parse LLM response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                logger.warning("LLM verification returned no JSON, assuming inputs are valid")
                return {
                    "verified_template": generated_template,
                    "verified_fields": extracted_fields,
                    "issues_found": [],
                    "confidence": 0.5,
                    "verification_status": "NO_VERIFICATION"
                }
            
            verification = json.loads(json_match.group())
            
            # Process verification results
            verified_template = generated_template
            verified_fields = extracted_fields.copy() if extracted_fields else {}
            issues_found = []
            
            # Handle template cleaning
            if verification.get("template_needs_cleaning", False):
                template_issues = verification.get("template_issues", [])
                issues_found.extend(template_issues)
                
                # Check if template contains nested JSON
                if any("JSON" in issue or "nested" in issue.lower() for issue in template_issues):
                    try:
                        # Try to extract the actual template from nested structure
                        temp_parsed = json.loads(generated_template)
                        if isinstance(temp_parsed, dict) and "generated_template" in temp_parsed:
                            verified_template = temp_parsed["generated_template"]
                            issues_found.append("FIXED: Extracted template from nested JSON structure")
                            logger.info("LLM detected and fixed nested JSON in template")
                    except:
                        pass
                
                # Unescape common escape sequences if present
                if any("escape" in issue.lower() or "\\n" in issue for issue in template_issues):
                    verified_template = verified_template.replace("\\n", "\n").replace("\\t", "\t").replace('\\"', '"')
                    issues_found.append("FIXED: Unescaped special characters in template")
                    logger.info("LLM detected and fixed escaped characters")
            
            # Handle fields cleaning
            if verification.get("fields_need_cleaning", False):
                fields_issues = verification.get("fields_issues", [])
                issues_found.extend(fields_issues)
                
                # Apply LLM suggestions if provided
                cleaned_suggestions = verification.get("cleaned_fields_suggestions", {})
                if cleaned_suggestions:
                    for key, suggested_value in cleaned_suggestions.items():
                        if key in verified_fields:
                            old_value = verified_fields[key]
                            verified_fields[key] = suggested_value
                            issues_found.append(f"FIXED: Updated field '{key}' from '{old_value}' to '{suggested_value}'")
                            logger.info(f"LLM suggested field update: {key}")
            
            confidence = verification.get("confidence", 0.7)
            recommendation = verification.get("recommendation", "PROCEED")
            
            return {
                "verified_template": verified_template,
                "verified_fields": verified_fields,
                "issues_found": issues_found,
                "confidence": confidence,
                "recommendation": recommendation,
                "verification_status": "VERIFIED",
                "summary": verification.get("summary", "Verification completed")
            }
            
        except Exception as e:
            logger.error(f"Error in LLM verification: {str(e)}")
            # On error, return inputs as-is
            return {
                "verified_template": generated_template,
                "verified_fields": extracted_fields,
                "issues_found": [f"Verification error: {str(e)}"],
                "confidence": 0.3,
                "verification_status": "ERROR",
                "recommendation": "PROCEED"
            }
    
    def check_quality(
        self,
        generated_template: str,
        extracted_fields: dict,
        document_type: str,
        iso_standard: str,
        quality_rules: str
    ) -> dict:
        """
        Check the quality of a generated ISO template against quality rules.
        
        Args:
            generated_template: The generated template to check
            extracted_fields: Fields used to generate the template (can be None or empty dict)
            document_type: Type of document
            iso_standard: ISO standard followed
            quality_rules: Formatted quality rules text
            
        Returns:
            Dictionary containing quality check results
        """
        try:
            # Handle None or empty extracted_fields
            if extracted_fields is None:
                extracted_fields = {}
            
            # Prepare fields for prompt
            fields_available = len(extracted_fields) > 0
            if fields_available:
                fields_text = "\n".join([f"- {key}: {value}" for key, value in extracted_fields.items()])
            else:
                fields_text = "(No extracted fields provided - field-specific validation will be limited)"
            
            prompt = f"""You are a quality assurance expert specializing in ISO documentation.

Analyze the following generated ISO document template against the provided quality rules.

DOCUMENT INFORMATION:
- Document Type: {document_type}
- ISO Standard: {iso_standard}

EXTRACTED FIELDS:
{fields_text}

GENERATED TEMPLATE:
{generated_template}

QUALITY RULES TO CHECK:
{quality_rules}

For each rule, evaluate whether the template passes or fails. Pay special attention to:
- Department field being "Not found", "N/A", empty, or containing generic text
- Dates older than 2 years from today's date ({datetime.now().strftime('%Y-%m-%d')})
- Missing required fields or sections
- Placeholder text or incomplete content

{"NOTE: Since no extracted fields were provided, focus primarily on structural and content quality rules. Field-specific rules (QR001, QR003, QR004, QR007, QR014) should be evaluated based only on what appears in the template itself." if not fields_available else ""}

Provide your analysis in the following JSON format:
{{
  "violations": [
    {{
      "rule_id": "QR001",
      "rule_name": "Rule Name",
      "severity": "error",
      "description": "What this rule checks",
      "violation_details": "Specific details of what failed or passed",
      "passed": false
    }}
  ],
  "recommendations": [
    "Specific recommendation 1",
    "Specific recommendation 2"
  ]
}}

Return ONLY the JSON object, no additional text."""

            model = self._get_model()
            response = model.generate_text(prompt=prompt)
            
            # Parse the response
            import json
            import re
            
            # Ensure response is not None
            if response is None:
                logger.error("LLM returned None response")
                return {
                    "violations": [],
                    "recommendations": ["LLM returned empty response. Please try again."]
                }
            
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    # Ensure result has the required structure
                    if not isinstance(result, dict):
                        logger.error(f"LLM returned non-dict JSON: {type(result)}")
                        result = {
                            "violations": [],
                            "recommendations": ["LLM returned invalid response format."]
                        }
                    else:
                        # Ensure required keys exist
                        if "violations" not in result:
                            result["violations"] = []
                        if "recommendations" not in result:
                            result["recommendations"] = []
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON from LLM response: {e}")
                    result = {
                        "violations": [],
                        "recommendations": ["Failed to parse quality check results. Please review manually."]
                    }
            else:
                # If no JSON found, create a basic result
                logger.warning("No JSON found in LLM response")
                result = {
                    "violations": [],
                    "recommendations": ["Unable to parse quality check results. Please review manually."]
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error checking quality: {str(e)}")
            raise
    
    def simple_quality_check(self, generated_template: str) -> str:
        """
        Simple quality check that takes a generated ISO template and returns an LLM-generated quality report.
        No complex typing, no validation errors - just pure simplicity.
        
        Args:
            generated_template: The generated ISO template to analyze for quality
            
        Returns:
            str: A comprehensive quality report generated by the LLM
        """
        try:
            prompt = f"""You are a quality assurance expert for ISO compliance documents.

Analyze the following generated ISO template for quality and compliance issues:

GENERATED ISO TEMPLATE:
{generated_template}

Please provide a comprehensive quality assessment report that includes:
1. Overall Quality Score (0-100)
2. Quality Grade (A, B, C, D, or F)
3. Key Strengths
4. Critical Issues Found
5. Areas for Improvement
6. Specific Recommendations
7. ISO Compliance Status
8. Formatting and Structure Assessment

Format your response as a clear, professional quality report."""

            model = self._get_model()
            response = model.generate_text(prompt=prompt)
            
            if not response:
                logger.error("LLM returned empty response for simple quality check")
                return "Error: Unable to generate quality report. Please try again."
            
            logger.info(f"Simple quality check completed. Response length: {len(response)} chars")
            return response
            
        except Exception as e:
            logger.error(f"Error in simple quality check: {str(e)}")
            return f"Error generating quality report: {str(e)}"


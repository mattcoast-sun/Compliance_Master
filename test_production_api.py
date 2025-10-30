"""
Comprehensive test suite for Compliance Master API
Tests all endpoints on the production Railway deployment
"""
import requests
import pytest
import json
from pathlib import Path
import time

# Production API configuration
BASE_URL = "https://compliancemaster-production.up.railway.app"
TIMEOUT = 120  # Standard timeout for single AI operations
WORKFLOW_TIMEOUT = 300  # Extended timeout for complete workflows (5 minutes)


class TestSystemEndpoints:
    """Test system health and status endpoints"""
    
    def test_health_check(self):
        """Test GET /health endpoint"""
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        print(f"✅ Health check passed - Version: {data['version']}")
    
    def test_list_preloaded_documents(self):
        """Test GET /api/v1/list-preloaded-documents endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/v1/list-preloaded-documents",
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "available_documents" in data
        assert "message" in data
        assert len(data["available_documents"]) > 0
        
        # Verify document structure
        for doc in data["available_documents"]:
            assert "document_id" in doc
            assert "description" in doc
            assert "filename" in doc
        
        print(f"✅ Found {len(data['available_documents'])} pre-loaded documents")
        for doc in data["available_documents"]:
            print(f"   - {doc['document_id']}: {doc['description']}")


class TestDocumentProcessing:
    """Test individual document processing steps"""
    
    @pytest.fixture
    def sample_docx_file(self):
        """Provide path to sample DOCX file"""
        path = Path("sample_device_calibration_procedure.docx")
        if not path.exists():
            pytest.skip("Sample DOCX file not found")
        return path
    
    def test_parse_document(self, sample_docx_file):
        """Test POST /api/v1/parse-document endpoint"""
        with open(sample_docx_file, 'rb') as f:
            files = {'file': (sample_docx_file.name, f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            response = requests.post(
                f"{BASE_URL}/api/v1/parse-document",
                files=files,
                timeout=TIMEOUT
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "extracted_text" in data
        assert "metadata" in data
        assert len(data["extracted_text"]) > 0
        
        print(f"✅ Document parsed - Extracted {len(data['extracted_text'])} characters")
    
    def test_extract_fields(self, sample_docx_file):
        """Test POST /api/v1/extract-fields endpoint"""
        # First parse the document to get text
        with open(sample_docx_file, 'rb') as f:
            files = {'file': (sample_docx_file.name, f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            parse_response = requests.post(
                f"{BASE_URL}/api/v1/parse-document",
                files=files,
                timeout=TIMEOUT
            )
        
        extracted_text = parse_response.json()["extracted_text"]
        
        # Now extract fields
        payload = {
            "document_text": extracted_text,
            "fields_to_extract": [
                "document_title",
                "document_number",
                "revision_number",
                "effective_date",
                "department"
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/extract-fields",
            json=payload,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "extracted_fields" in data
        assert len(data["extracted_fields"]) > 0
        
        # Verify field structure
        for field in data["extracted_fields"]:
            assert "field_name" in field
            assert "value" in field
            assert "confidence" in field
        
        print(f"✅ Extracted {len(data['extracted_fields'])} fields")
        for field in data["extracted_fields"]:
            print(f"   - {field['field_name']}: {field['value']}")
    
    def test_generate_iso_template(self):
        """Test POST /api/v1/generate-iso-template endpoint"""
        payload = {
            "document_type": "quality_system_record",
            "extracted_fields": {
                "document_title": "Test Quality System Procedure",
                "document_number": "QSP-TEST-001",
                "revision_number": "1.0",
                "effective_date": "2025-10-30",
                "department": "Quality Assurance",
                "author": "Test Author",
                "purpose": "Testing ISO template generation",
                "scope": "Test scope for validation"
            },
            "iso_standard": "ISO 9001:2015"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/generate-iso-template",
            json=payload,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "generated_template" in data
        assert data["document_type"] == "quality_system_record"
        assert data["iso_standard"] == "ISO 9001:2015"
        assert len(data["generated_template"]) > 100
        
        print(f"✅ Generated ISO template - Length: {len(data['generated_template'])} chars")
        print(f"   Preview: {data['generated_template'][:200]}...")


class TestCompleteProcessing:
    """Test complete processing pipelines"""
    
    @pytest.fixture
    def sample_docx_file(self):
        """Provide path to sample DOCX file"""
        path = Path("sample_device_calibration_procedure.docx")
        if not path.exists():
            pytest.skip("Sample DOCX file not found")
        return path
    
    def test_process_preloaded_sample_calibration(self):
        """Test POST /api/v1/process-preloaded with sample_calibration"""
        payload = {
            "document_id": "sample_calibration",
            "iso_standard": "ISO 9001:2015",
            "document_type": "quality_system_record"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/process-preloaded",
            json=payload,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "generated_template" in data
        assert data["document_type"] == "quality_system_record"
        assert data["iso_standard"] == "ISO 9001:2015"
        
        print("✅ Processed pre-loaded 'sample_calibration' document")
        print(f"   Template length: {len(data['generated_template'])} chars")
    
    def test_process_preloaded_non_compliant(self):
        """Test POST /api/v1/process-preloaded with non_compliant_iso"""
        payload = {
            "document_id": "non_compliant_iso",
            "iso_standard": "ISO 9001:2015",
            "document_type": "quality_system_record"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/process-preloaded",
            json=payload,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "generated_template" in data
        
        print("✅ Processed pre-loaded 'non_compliant_iso' document")
        print(f"   Template length: {len(data['generated_template'])} chars")
    
    def test_process_preloaded_invalid_id(self):
        """Test POST /api/v1/process-preloaded with invalid document_id"""
        payload = {
            "document_id": "invalid_document_id",
            "iso_standard": "ISO 9001:2015",
            "document_type": "quality_system_record"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/process-preloaded",
            json=payload,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        print("✅ Invalid document_id correctly rejected")
    
    def test_process_complete_with_file(self, sample_docx_file):
        """Test POST /api/v1/process-complete with file upload"""
        with open(sample_docx_file, 'rb') as f:
            files = {'file': (sample_docx_file.name, f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            data = {
                'iso_standard': 'ISO 9001:2015',
                'document_type': 'quality_system_record'
            }
            response = requests.post(
                f"{BASE_URL}/api/v1/process-complete",
                files=files,
                data=data,
                timeout=TIMEOUT
            )
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "generated_template" in result
        assert "extracted_fields" in result  # NEW: Check for extracted_fields
        assert result["document_type"] == "quality_system_record"
        
        print("✅ Complete processing pipeline with file upload succeeded")
        print(f"   Template length: {len(result['generated_template'])} chars")
        print(f"   Extracted fields: {len(result['extracted_fields'])} fields")  # NEW


class TestQualityAssurance:
    """Test quality checking functionality"""
    
    def test_check_quality_compliant(self):
        """Test POST /api/v1/check-quality with compliant template"""
        # Create a good template
        template = """=== QUALITY SYSTEM RECORD ===

Document Title: Quality System Procedure
Document Number: QSP-001
Revision Number: 2.0
Effective Date: 2025-10-30
Department: Quality Assurance
Author: John Doe

PURPOSE:
This document establishes the quality system procedures for our organization.

SCOPE:
This procedure applies to all quality management activities.

PROCEDURE:
1. Document control procedures
2. Quality audit procedures
3. Corrective action procedures

RESPONSIBILITIES:
Quality Manager: Overall responsibility for quality system
Department Heads: Implementation in their areas

REFERENCES:
- ISO 9001:2015
- Internal Quality Manual

REVISION HISTORY:
Rev 1.0 - 2024-01-15 - Initial release
Rev 2.0 - 2025-10-30 - Updated procedures
"""
        
        payload = {
            "generated_template": template,
            "extracted_fields": {
                "document_title": "Quality System Procedure",
                "document_number": "QSP-001",
                "department": "Quality Assurance",
                "effective_date": "2025-10-30"
            },
            "document_type": "quality_system_record",
            "iso_standard": "ISO 9001:2015"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/check-quality",
            json=payload,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "overall_score" in data
        assert "quality_grade" in data
        assert "violations" in data
        assert data["quality_grade"] in ["A", "B", "C", "D", "F"]
        
        print(f"✅ Quality check completed")
        print(f"   Score: {data['overall_score']:.1f}/100")
        print(f"   Grade: {data['quality_grade']}")
        print(f"   Rules checked: {data['total_rules_checked']}")
        print(f"   Passed: {data['rules_passed']}, Failed: {data['rules_failed']}")
    
    def test_check_quality_non_compliant(self):
        """Test POST /api/v1/check-quality with non-compliant template"""
        # Create a poor template (missing key fields)
        template = """Simple Document

This is a basic document without proper structure.
It's missing many required fields.
"""
        
        payload = {
            "generated_template": template,
            "extracted_fields": {},
            "document_type": "quality_system_record",
            "iso_standard": "ISO 9001:2015"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/check-quality",
            json=payload,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["rules_failed"] > 0  # Should have violations
        
        print(f"✅ Non-compliant template correctly identified")
        print(f"   Score: {data['overall_score']:.1f}/100")
        print(f"   Grade: {data['quality_grade']}")
        print(f"   Violations found: {data['rules_failed']}")
    
    def test_check_quality_with_null_extracted_fields(self):
        """Test POST /api/v1/check-quality with null extracted_fields (regression test for NoneType error)"""
        # Create a template
        template = """=== QUALITY SYSTEM RECORD ===

Document Title: Quality System Procedure
Document Number: QSP-001
Revision Number: 2.0
Effective Date: 2025-10-30
Department: Quality Assurance

PURPOSE:
This document establishes the quality system procedures.

SCOPE:
This procedure applies to all quality management activities.
"""
        
        # Test with null extracted_fields
        payload = {
            "generated_template": template,
            "extracted_fields": None,
            "document_type": "quality_system_record",
            "iso_standard": "ISO 9001:2015"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/check-quality",
            json=payload,
            timeout=TIMEOUT
        )
        
        # Should succeed without validation error
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "overall_score" in data
        assert "quality_grade" in data
        
        print(f"✅ Quality check with null extracted_fields succeeded (bug fixed)")
        print(f"   Score: {data['overall_score']:.1f}/100")
        print(f"   Grade: {data['quality_grade']}")
    
    def test_check_quality_without_extracted_fields(self):
        """Test POST /api/v1/check-quality without extracted_fields field at all"""
        template = """=== QUALITY SYSTEM RECORD ===

Document Title: Test Document
Document Number: TST-001

PURPOSE:
Testing without extracted_fields parameter.
"""
        
        # Test without extracted_fields in payload
        payload = {
            "generated_template": template,
            "document_type": "quality_system_record",
            "iso_standard": "ISO 9001:2015"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/check-quality",
            json=payload,
            timeout=TIMEOUT
        )
        
        # Should succeed with default empty dict
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        print(f"✅ Quality check without extracted_fields parameter succeeded")
        print(f"   Score: {data['overall_score']:.1f}/100")


class TestCompleteWorkflow:
    """Test complete end-to-end workflows"""
    
    @pytest.fixture
    def sample_docx_file(self):
        """Provide path to sample DOCX file"""
        path = Path("sample_device_calibration_procedure.docx")
        if not path.exists():
            pytest.skip("Sample DOCX file not found")
        return path
    
    def test_workflow_preloaded_sample_calibration(self):
        """Test POST /api/v1/workflow-preloaded with sample_calibration"""
        payload = {
            "document_id": "sample_calibration",
            "iso_standard": "ISO 9001:2015",
            "document_type": "quality_system_record"
        }
        
        print("⏳ Running complete workflow (this may take 2-5 minutes)...")
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/api/v1/workflow-preloaded",
            json=payload,
            timeout=WORKFLOW_TIMEOUT
        )
        
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify all workflow components
        assert "extracted_text" in data
        assert "extracted_fields" in data
        assert "generated_template" in data
        assert "quality_score" in data
        assert "quality_grade" in data
        assert "violations" in data
        assert "recommendations" in data
        
        print(f"✅ Complete workflow succeeded in {elapsed_time:.1f}s")
        print(f"   Extracted text: {len(data['extracted_text'])} chars")
        print(f"   Extracted fields: {len(data['extracted_fields'])} fields")
        print(f"   Template: {len(data['generated_template'])} chars")
        print(f"   Quality score: {data['quality_score']:.1f}/100 (Grade: {data['quality_grade']})")
        print(f"   Rules: {data['rules_passed']} passed, {data['rules_failed']} failed")
    
    def test_workflow_preloaded_non_compliant(self):
        """Test POST /api/v1/workflow-preloaded with non_compliant_iso"""
        payload = {
            "document_id": "non_compliant_iso",
            "iso_standard": "ISO 9001:2015",
            "document_type": "quality_system_record"
        }
        
        print("⏳ Running workflow on non-compliant document (this may take 2-5 minutes)...")
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/api/v1/workflow-preloaded",
            json=payload,
            timeout=WORKFLOW_TIMEOUT
        )
        
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # This document should likely have quality issues
        print(f"✅ Workflow completed in {elapsed_time:.1f}s")
        print(f"   Quality score: {data['quality_score']:.1f}/100 (Grade: {data['quality_grade']})")
        print(f"   Violations: {data['rules_failed']}")
        
        if data["recommendations"]:
            print(f"   Recommendations:")
            for rec in data["recommendations"][:3]:  # Show first 3
                print(f"     - {rec}")
    
    def test_workflow_complete_with_file(self, sample_docx_file):
        """Test POST /api/v1/workflow-complete with file upload"""
        print("⏳ Running complete workflow with file upload (this may take 2-5 minutes)...")
        start_time = time.time()
        
        with open(sample_docx_file, 'rb') as f:
            files = {'file': (sample_docx_file.name, f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            data = {
                'iso_standard': 'ISO 9001:2015',
                'document_type': 'quality_system_record'
            }
            response = requests.post(
                f"{BASE_URL}/api/v1/workflow-complete",
                files=files,
                data=data,
                timeout=WORKFLOW_TIMEOUT
            )
        
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        
        # Verify all workflow components
        assert "extracted_text" in result
        assert "extracted_fields" in result
        assert "generated_template" in result
        assert "quality_score" in result
        
        print(f"✅ Complete workflow with upload succeeded in {elapsed_time:.1f}s")
        print(f"   Quality score: {result['quality_score']:.1f}/100 (Grade: {result['quality_grade']})")


class TestDebugEndpoint:
    """Test debug endpoint"""
    
    def test_debug_upload_no_file(self):
        """Test POST /api/v1/debug-upload without file"""
        data = {
            'iso_standard': 'ISO 9001:2015',
            'document_type': 'quality_system_record'
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/debug-upload",
            data=data,
            timeout=10
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "received" in result
        assert result["received"]["file"]["provided"] is False
        assert result["received"]["iso_standard"] == "ISO 9001:2015"
        
        print("✅ Debug endpoint working")


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_extract_fields_empty_text(self):
        """Test extract-fields with empty text"""
        payload = {
            "document_text": "",
            "fields_to_extract": ["document_title"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/extract-fields",
            json=payload,
            timeout=TIMEOUT
        )
        
        # Accept either 400 (validation error) or 500 (LLM service error on empty input)
        assert response.status_code in [400, 500]
        print(f"✅ Empty text correctly rejected (status: {response.status_code})")
    
    def test_generate_template_empty_fields(self):
        """Test generate-iso-template with empty fields"""
        payload = {
            "document_type": "quality_system_record",
            "extracted_fields": {},
            "iso_standard": "ISO 9001:2015"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/generate-iso-template",
            json=payload,
            timeout=TIMEOUT
        )
        
        # Accept either 400 (validation error) or 500 (LLM service error on empty input)
        assert response.status_code in [400, 500]
        print(f"✅ Empty fields correctly rejected (status: {response.status_code})")
    
    def test_check_quality_empty_template(self):
        """Test check-quality with empty template"""
        payload = {
            "generated_template": "",
            "extracted_fields": {},
            "document_type": "quality_system_record",
            "iso_standard": "ISO 9001:2015"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/check-quality",
            json=payload,
            timeout=TIMEOUT
        )
        
        # Accept either 400 (validation error) or 500 (LLM service error on empty input)
        assert response.status_code in [400, 500]
        print(f"✅ Empty template correctly rejected (status: {response.status_code})")


def run_all_tests():
    """Run all tests with pytest"""
    pytest.main([
        __file__,
        "-v",  # Verbose
        "-s",  # Show print statements
        "--tb=short",  # Short traceback format
        "--color=yes"  # Colored output
    ])


if __name__ == "__main__":
    print("=" * 80)
    print("COMPLIANCE MASTER API - COMPREHENSIVE TEST SUITE")
    print(f"Testing: {BASE_URL}")
    print("=" * 80)
    print()
    
    # Run tests
    run_all_tests()


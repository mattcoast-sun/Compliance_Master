#!/usr/bin/env python3
"""
Test script for Quality Check endpoint fixes
Tests all scenarios: null, missing, empty, and populated extracted_fields
"""
import requests
import json
from typing import Optional, Dict

API_BASE_URL = "http://localhost:8765"

# Sample template for testing
SAMPLE_TEMPLATE = """
=== QUALITY SYSTEM RECORD ===

Document Title: Equipment Calibration Procedure
Document Number: QSP-CAL-001
Revision Number: 2.0
Effective Date: 2025-10-30

Department: Quality Assurance
Author: John Doe

PURPOSE:
This procedure establishes the requirements for calibrating laboratory equipment.

SCOPE:
This procedure applies to all measuring and testing equipment used in quality control.

DEFINITIONS:
- Calibration: Process of verifying and adjusting measurement accuracy
- Traceability: Ability to relate measurements to known standards

PROCEDURE:
1. Identify equipment requiring calibration
2. Schedule calibration at appropriate intervals
3. Perform calibration using certified standards
4. Document calibration results
5. Apply calibration labels

RESPONSIBILITIES:
- Quality Manager: Approve calibration schedule
- Lab Technicians: Perform calibrations
- Calibration Coordinator: Maintain calibration records

RELATED DOCUMENTS:
- ISO 9001:2015 Quality Management System
- Equipment Inventory List (QF-EQ-001)

REVISION HISTORY:
Rev 2.0 - 2025-10-30 - Updated calibration intervals
Rev 1.0 - 2024-01-15 - Initial release
"""

def print_test_header(test_name: str):
    """Print formatted test header"""
    print("\n" + "="*70)
    print(f"TEST: {test_name}")
    print("="*70)

def test_quality_check(
    scenario: str,
    template: str,
    extracted_fields: Optional[Dict[str, str]] = None,
    document_type: str = "quality_system_record",
    iso_standard: str = "ISO 9001:2015",
    send_extracted_fields: bool = True
):
    """
    Test the quality check endpoint with different scenarios
    
    Args:
        scenario: Description of test scenario
        template: ISO template to check
        extracted_fields: Fields dict, None, or omit
        document_type: Document type
        iso_standard: ISO standard
        send_extracted_fields: Whether to include extracted_fields in request
    """
    print_test_header(scenario)
    
    # Build request payload
    payload = {
        "generated_template": template,
        "document_type": document_type,
        "iso_standard": iso_standard
    }
    
    # Conditionally add extracted_fields
    if send_extracted_fields:
        payload["extracted_fields"] = extracted_fields
    
    print(f"\n📤 REQUEST PAYLOAD:")
    print(f"  - generated_template: {len(template)} characters")
    print(f"  - document_type: {document_type}")
    print(f"  - iso_standard: {iso_standard}")
    
    if send_extracted_fields:
        if extracted_fields is None:
            print(f"  - extracted_fields: null")
        elif len(extracted_fields) == 0:
            print(f"  - extracted_fields: {{}} (empty dict)")
        else:
            print(f"  - extracted_fields: {len(extracted_fields)} fields")
    else:
        print(f"  - extracted_fields: (not sent)")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/check-quality",
            json=payload,
            timeout=60
        )
        
        print(f"\n📥 RESPONSE:")
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ SUCCESS")
            print(f"  - Quality Grade: {data.get('quality_grade')}")
            print(f"  - Overall Score: {data.get('overall_score'):.1f}%")
            print(f"  - Total Rules Checked: {data.get('total_rules_checked')}")
            print(f"  - Rules Passed: {data.get('rules_passed')}")
            print(f"  - Rules Failed: {data.get('rules_failed')}")
            print(f"  - Message: {data.get('message')}")
            
            if data.get('violations'):
                print(f"\n  📋 VIOLATIONS SAMPLE (first 3):")
                for v in data['violations'][:3]:
                    status = "✅ PASSED" if v['passed'] else "❌ FAILED"
                    print(f"    - [{v['rule_id']}] {v['rule_name']}: {status}")
            
            return True
        else:
            print(f"  ❌ FAILED")
            print(f"  Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n  ❌ CONNECTION ERROR")
        print(f"  Is the API server running at {API_BASE_URL}?")
        print(f"  Start it with: ./run.sh")
        return False
    except Exception as e:
        print(f"\n  ❌ EXCEPTION: {str(e)}")
        return False

def test_chaining():
    """Test chaining from ISO template generation to quality check"""
    print_test_header("CHAINING: ISO Template Generation → Quality Check")
    
    print("\n📤 STEP 1: Generate ISO Template")
    
    # Step 1: Generate template
    template_request = {
        "document_type": "quality_system_record",
        "extracted_fields": {
            "document_title": "Calibration Procedure",
            "document_number": "QSP-001",
            "revision_number": "1.0",
            "effective_date": "2025-10-30",
            "department": "Quality Assurance",
            "author": "Test User",
            "purpose": "Define calibration process",
            "scope": "All lab equipment"
        },
        "iso_standard": "ISO 9001:2015"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/generate-iso-template",
            json=template_request,
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"  ❌ Template generation failed: {response.text}")
            return False
        
        template_data = response.json()
        print(f"  ✅ Template generated successfully")
        print(f"  - Generated template: {len(template_data['generated_template'])} characters")
        print(f"  - Extracted fields: {len(template_data.get('extracted_fields', {}))} fields")
        
        # Step 2: Chain to quality check
        print(f"\n📤 STEP 2: Check Quality (using template output)")
        
        quality_request = {
            "generated_template": template_data["generated_template"],
            "extracted_fields": template_data.get("extracted_fields"),
            "document_type": template_data["document_type"],
            "iso_standard": template_data["iso_standard"]
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/check-quality",
            json=quality_request,
            timeout=60
        )
        
        if response.status_code == 200:
            quality_data = response.json()
            print(f"  ✅ Quality check completed")
            print(f"  - Quality Grade: {quality_data.get('quality_grade')}")
            print(f"  - Total Rules Checked: {quality_data.get('total_rules_checked')}")
            print(f"  - Rules Passed: {quality_data.get('rules_passed')}")
            return True
        else:
            print(f"  ❌ Quality check failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"  ❌ EXCEPTION: {str(e)}")
        return False

def main():
    """Run all test scenarios"""
    print("\n")
    print("🧪 QUALITY CHECK ENDPOINT - COMPREHENSIVE TESTS")
    print("=" * 70)
    print("Testing fixes for: 'NoneType' object has no attribute 'items'")
    print("=" * 70)
    
    results = {}
    
    # Test 1: With populated extracted_fields
    results["populated_fields"] = test_quality_check(
        scenario="Scenario 1: Populated extracted_fields",
        template=SAMPLE_TEMPLATE,
        extracted_fields={
            "document_title": "Equipment Calibration Procedure",
            "document_number": "QSP-CAL-001",
            "department": "Quality Assurance",
            "author": "John Doe"
        }
    )
    
    # Test 2: With empty dict
    results["empty_dict"] = test_quality_check(
        scenario="Scenario 2: Empty extracted_fields dict",
        template=SAMPLE_TEMPLATE,
        extracted_fields={}
    )
    
    # Test 3: With explicit null
    results["explicit_null"] = test_quality_check(
        scenario="Scenario 3: Explicit null extracted_fields",
        template=SAMPLE_TEMPLATE,
        extracted_fields=None
    )
    
    # Test 4: Field omitted completely
    results["omitted_field"] = test_quality_check(
        scenario="Scenario 4: extracted_fields omitted (not sent)",
        template=SAMPLE_TEMPLATE,
        send_extracted_fields=False
    )
    
    # Test 5: Chaining
    results["chaining"] = test_chaining()
    
    # Summary
    print("\n")
    print("="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASSED" if passed_test else "❌ FAILED"
        print(f"  {status}  {test_name.replace('_', ' ').title()}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! The fixes are working correctly!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review the output above.")
    
    print("="*70)

if __name__ == "__main__":
    main()


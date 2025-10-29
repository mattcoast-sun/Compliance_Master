"""
Example usage of the Compliance Master API
"""
import requests
import json


BASE_URL = "http://localhost:8765"


def test_health_check():
    """Test the health check endpoint"""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200


def test_parse_document(file_path: str):
    """Test document parsing endpoint"""
    print("\n=== Testing Document Parsing ===")
    
    with open(file_path, 'rb') as f:
        files = {'file': (file_path, f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
        response = requests.post(f"{BASE_URL}/api/v1/parse-document", files=files)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Message: {data['message']}")
        print(f"Metadata: {data['metadata']}")
        print(f"Text length: {len(data['extracted_text'])} characters")
        print(f"Text preview: {data['extracted_text'][:200]}...")
        return data
    else:
        print(f"Error: {response.text}")
        return None


def test_extract_fields(document_text: str):
    """Test field extraction endpoint"""
    print("\n=== Testing Field Extraction ===")
    
    payload = {
        "document_text": document_text,
        "fields_to_extract": [
            "document_title",
            "document_number",
            "revision_number",
            "effective_date",
            "department",
            "author",
            "purpose",
            "scope"
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/extract-fields",
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Message: {data['message']}")
        print("\nExtracted Fields:")
        for field in data['extracted_fields']:
            print(f"  - {field['field_name']}: {field['value']} (confidence: {field['confidence']})")
        return data
    else:
        print(f"Error: {response.text}")
        return None


def test_generate_iso_template(extracted_fields: dict):
    """Test ISO template generation endpoint"""
    print("\n=== Testing ISO Template Generation ===")
    
    # Convert extracted fields list to dict
    fields_dict = {field['field_name']: field['value'] for field in extracted_fields}
    
    payload = {
        "document_type": "quality_system_record",
        "extracted_fields": fields_dict,
        "iso_standard": "ISO 9001:2015"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/generate-iso-template",
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Message: {data['message']}")
        print(f"Document Type: {data['document_type']}")
        print(f"ISO Standard: {data['iso_standard']}")
        print(f"\nGenerated Template Preview:")
        print(data['generated_template'][:500] + "...")
        return data
    else:
        print(f"Error: {response.text}")
        return None


def test_complete_pipeline(file_path: str):
    """Test complete processing pipeline"""
    print("\n=== Testing Complete Pipeline ===")
    
    with open(file_path, 'rb') as f:
        files = {'file': (file_path, f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
        data = {
            'iso_standard': 'ISO 9001:2015',
            'document_type': 'quality_system_record'
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/process-complete",
            files=files,
            data=data
        )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Message: {data['message']}")
        print(f"Document Type: {data['document_type']}")
        print(f"ISO Standard: {data['iso_standard']}")
        print(f"\nGenerated Template Preview:")
        print(data['generated_template'][:500] + "...")
        return data
    else:
        print(f"Error: {response.text}")
        return None


def test_quality_check(generated_template: str, extracted_fields: dict, document_type: str = "quality_system_record", iso_standard: str = "ISO 9001:2015"):
    """Test quality check endpoint"""
    print("\n=== Testing Quality Check ===")
    
    # Convert extracted fields list to dict if needed
    if isinstance(extracted_fields, list):
        fields_dict = {field['field_name']: field['value'] for field in extracted_fields}
    else:
        fields_dict = extracted_fields
    
    payload = {
        "generated_template": generated_template,
        "extracted_fields": fields_dict,
        "document_type": document_type,
        "iso_standard": iso_standard
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/check-quality",
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Message: {data['message']}")
        print(f"\nQuality Assessment:")
        print(f"  Overall Score: {data['overall_score']:.2f}/100")
        print(f"  Quality Grade: {data['quality_grade']}")
        print(f"  Total Rules Checked: {data['total_rules_checked']}")
        print(f"  Rules Passed: {data['rules_passed']}")
        print(f"  Rules Failed: {data['rules_failed']}")
        
        print(f"\n  Violations Found:")
        if data['violations']:
            for violation in data['violations']:
                status_icon = "✓" if violation['passed'] else "✗"
                print(f"    {status_icon} [{violation['rule_id']}] {violation['rule_name']} ({violation['severity']})")
                print(f"       {violation['violation_details']}")
        else:
            print("    No violations found!")
        
        if data['recommendations']:
            print(f"\n  Recommendations:")
            for i, rec in enumerate(data['recommendations'], 1):
                print(f"    {i}. {rec}")
        
        print(f"\n  Report saved to: {data['saved_file_path']}")
        return data
    else:
        print(f"Error: {response.text}")
        return None


def main():
    """Main function to run all tests"""
    print("=" * 60)
    print("Compliance Master API - Example Usage")
    print("=" * 60)
    
    # Test health check
    if not test_health_check():
        print("\nERROR: API is not healthy. Please check if the server is running.")
        return
    
    # Example file path (update this with your actual file)
    file_path = "/Users/mattiasacosta/Documents/Programming_Projects/Compliance_Master/sample_device_calibration_procedure.docx"
    
    print("\nNOTE: To test the full pipeline, provide a valid DOCX file path.")
    print(f"Current file path: {file_path}")
    print("\nUncomment the following sections in the code to test with a real file:")
    
    # Test individual endpoints
    parse_result = test_parse_document(file_path)
    if parse_result:
        extraction_result = test_extract_fields(parse_result['extracted_text'])
        if extraction_result:
            template_result = test_generate_iso_template(extraction_result['extracted_fields'])
            
            # Test quality check on the generated template
            if template_result:
                test_quality_check(
                    generated_template=template_result['generated_template'],
                    extracted_fields=extraction_result['extracted_fields'],
                    document_type=template_result['document_type'],
                    iso_standard=template_result['iso_standard']
                )
    
    # Test complete pipeline
    complete_result = test_complete_pipeline(file_path)
    
    # Test quality check on complete pipeline result
    if complete_result:
        print("\n" + "=" * 60)
        print("Testing Quality Check on Complete Pipeline Output")
        print("=" * 60)
        
        # For complete pipeline, we need to extract the fields
        # Read the saved output to get the extracted_fields
        import json
        import os
        if 'saved_file_path' in complete_result and os.path.exists(complete_result['saved_file_path']):
            with open(complete_result['saved_file_path'], 'r') as f:
                saved_data = json.load(f)
                test_quality_check(
                    generated_template=complete_result['generated_template'],
                    extracted_fields=saved_data.get('extracted_fields', {}),
                    document_type=complete_result['document_type'],
                    iso_standard=complete_result['iso_standard']
                )
    
    print("\n" + "=" * 60)
    print("Example usage complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()


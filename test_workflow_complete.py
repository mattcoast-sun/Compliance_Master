"""
Test script for the complete workflow endpoint
"""
import requests
import json
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8765"
ENDPOINT = f"{API_BASE_URL}/api/v1/workflow-complete"

# Path to test document
TEST_DOCUMENT = "sample_device_calibration_procedure.docx"

def test_workflow_complete():
    """
    Test the complete workflow endpoint that executes all steps:
    1. Parse document
    2. Extract fields
    3. Generate ISO template
    4. Run quality check
    """
    print("=" * 80)
    print("Testing Complete Workflow Endpoint")
    print("=" * 80)
    
    # Check if test file exists
    if not Path(TEST_DOCUMENT).exists():
        print(f"Error: Test document '{TEST_DOCUMENT}' not found!")
        return
    
    print(f"\n📄 Uploading document: {TEST_DOCUMENT}")
    
    # Prepare the file upload
    with open(TEST_DOCUMENT, 'rb') as f:
        files = {
            'file': (TEST_DOCUMENT, f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        }
        
        # Optional parameters
        data = {
            'iso_standard': 'ISO 9001:2015',
            'document_type': 'quality_system_record'
        }
        
        print("\n🔄 Processing workflow (this may take a minute)...")
        print("  Step 1: Parsing document...")
        print("  Step 2: Extracting fields...")
        print("  Step 3: Generating ISO template...")
        print("  Step 4: Running quality check...")
        
        try:
            # Make the request
            response = requests.post(ENDPOINT, files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                
                print("\n" + "=" * 80)
                print("✅ Workflow Completed Successfully!")
                print("=" * 80)
                
                # Print summary information
                print(f"\n📊 RESULTS SUMMARY:")
                print(f"  Source Document: {result.get('source_document')}")
                print(f"  Document Type: {result.get('document_type')}")
                print(f"  ISO Standard: {result.get('iso_standard')}")
                print(f"  Timestamp: {result.get('timestamp')}")
                
                print(f"\n📝 EXTRACTED FIELDS ({len(result.get('extracted_fields', {}))} fields):")
                for field_name, field_value in result.get('extracted_fields', {}).items():
                    print(f"  • {field_name}: {field_value}")
                
                print(f"\n✨ GENERATED TEMPLATE (length: {len(result.get('generated_template', ''))} chars):")
                template_preview = result.get('generated_template', '')[:500]
                print(f"  {template_preview}...")
                
                print(f"\n🎯 QUALITY CHECK RESULTS:")
                print(f"  Overall Score: {result.get('quality_score'):.2f}/100")
                print(f"  Quality Grade: {result.get('quality_grade')}")
                print(f"  Rules Checked: {result.get('total_rules_checked')}")
                print(f"  Rules Passed: {result.get('rules_passed')} ✅")
                print(f"  Rules Failed: {result.get('rules_failed')} ❌")
                
                violations = result.get('violations', [])
                if violations:
                    print(f"\n⚠️  QUALITY VIOLATIONS:")
                    for v in violations:
                        status = "✅ PASS" if v['passed'] else "❌ FAIL"
                        severity = v['severity'].upper()
                        print(f"  [{status}] [{severity}] {v['rule_name']}")
                        if not v['passed']:
                            print(f"      {v['violation_details']}")
                
                recommendations = result.get('recommendations', [])
                if recommendations:
                    print(f"\n💡 RECOMMENDATIONS:")
                    for i, rec in enumerate(recommendations, 1):
                        print(f"  {i}. {rec}")
                
                if result.get('saved_file_path'):
                    print(f"\n💾 Results saved to: {result.get('saved_file_path')}")
                
                print("\n" + "=" * 80)
                
                # Save full results to a pretty-printed JSON file
                output_file = "test_workflow_complete_results.json"
                with open(output_file, 'w', encoding='utf-8') as out_f:
                    json.dump(result, out_f, indent=2, ensure_ascii=False)
                print(f"📁 Full response saved to: {output_file}")
                print("=" * 80)
                
            else:
                print(f"\n❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("\n❌ Error: Could not connect to API server.")
            print(f"Make sure the server is running at {API_BASE_URL}")
            print("Run: python main.py")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    test_workflow_complete()


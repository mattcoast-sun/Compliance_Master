"""
Test script for the new executive quality check endpoint
"""
import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8765"

# Sample generated template for testing
SAMPLE_TEMPLATE = """
ISO 9001:2015 Quality System Record

Document Information:
- Document Title: Device Calibration Procedure
- Document Number: QP-CAL-001
- Revision Number: 2.0
- Effective Date: January 15, 2022
- Department: Not found
- Author: John Smith

1. PURPOSE AND SCOPE
The purpose of this procedure is to establish a standardized method for calibrating 
measurement devices used in manufacturing operations to ensure accuracy and compliance 
with ISO 9001:2015 requirements.

2. DEFINITIONS AND REFERENCES
- Calibration: The process of verifying and adjusting device accuracy
- Reference Standard: NIST-traceable measurement standard
- Related Documents: QP-EQP-001 Equipment Management Procedure

3. PROCEDURE
3.1 Pre-calibration checks
3.2 Calibration execution
3.3 Post-calibration verification
3.4 Documentation

4. RESPONSIBILITIES
- Quality Manager: Overall responsibility for calibration program
- Calibration Technician: Execute calibration procedures
- Department Supervisor: Generic oversight

5. REVISION HISTORY
| Rev | Date | Description | Approved By |
|-----|------|-------------|-------------|
| 1.0 | 2021-01-10 | Initial release | J. Smith |
| 2.0 | 2022-01-15 | Updated procedure | J. Smith |
"""


def test_executive_quality_check():
    """Test the executive quality check endpoint"""
    
    print("=" * 80)
    print("Testing Executive Quality Check Endpoint")
    print("=" * 80)
    
    # Prepare request (ultra-simple - just one string field!)
    endpoint = f"{BASE_URL}/api/v1/quality-check-executive"
    payload = {
        "generated_template": SAMPLE_TEMPLATE
    }
    
    print(f"\n📤 Sending request to: {endpoint}")
    print(f"Template length: {len(SAMPLE_TEMPLATE)} characters")
    
    try:
        # Make request
        response = requests.post(endpoint, json=payload)
        
        print(f"\n📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n" + "=" * 80)
            print("✅ EXECUTIVE QUALITY REPORT")
            print("=" * 80)
            
            # Print the markdown report
            print(f"\n{result['quality_report']}")
            
            print("\n" + "=" * 80)
            print("✅ Test completed successfully!")
            print("=" * 80)
            print(f"\nTimestamp: {result['timestamp']}")
            print(f"Success: {result['success']}")
            
            # Save full response to file
            with open('executive_quality_check_test_result.json', 'w') as f:
                json.dump(result, f, indent=2)
            print("\n💾 Full response saved to: executive_quality_check_test_result.json")
            
            return True
            
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection Error: Could not connect to {BASE_URL}")
        print("   Make sure the API server is running:")
        print("   python main.py")
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_comparison():
    """Compare executive endpoint vs simple endpoint"""
    
    print("\n" + "=" * 80)
    print("COMPARISON: Executive vs Simple Quality Check")
    print("=" * 80)
    
    print("\n📤 Testing both endpoints with the same template...")
    
    try:
        # Test executive endpoint (just one string field!)
        exec_start = time.time()
        exec_response = requests.post(
            f"{BASE_URL}/api/v1/quality-check-executive",
            json={
                "generated_template": SAMPLE_TEMPLATE
            }
        )
        exec_time = time.time() - exec_start
        
        # Test simple endpoint
        simple_start = time.time()
        simple_response = requests.post(
            f"{BASE_URL}/api/v1/quality-check-simple",
            json={"generated_template": SAMPLE_TEMPLATE}
        )
        simple_time = time.time() - simple_start
        
        print("\n📊 COMPARISON RESULTS:")
        print("-" * 80)
        print(f"\n🏢 Executive Endpoint (/api/v1/quality-check-executive):")
        print(f"   Response time: {exec_time:.2f}s")
        print(f"   Status: {exec_response.status_code}")
        
        if exec_response.status_code == 200:
            exec_data = exec_response.json()
            report_length = len(exec_data.get('quality_report', ''))
            print(f"   Report length: {report_length} characters")
            print(f"   Output type: Structured markdown (tables, grades, sections)")
            print(f"   Format: Clean markdown with tables and lists")
        
        print(f"\n📝 Simple Endpoint (/api/v1/quality-check-simple):")
        print(f"   Response time: {simple_time:.2f}s")
        print(f"   Status: {simple_response.status_code}")
        
        if simple_response.status_code == 200:
            simple_data = simple_response.json()
            report_length = len(simple_data.get('quality_report', ''))
            print(f"   Report length: {report_length} characters")
            print(f"   Output type: Lengthy paragraph text")
            print(f"   Preview: {simple_data.get('quality_report', '')[:200]}...")
        
        print("\n" + "=" * 80)
        print("💡 KEY DIFFERENCES:")
        print("-" * 80)
        print("   Executive Endpoint:")
        print("      ✅ Structured markdown tables")
        print("      ✅ Section-by-section grades in table format")
        print("      ✅ Easy to scan and navigate")
        print("      ✅ Executive/auditor friendly")
        print("      ✅ Concise, actionable insights")
        print("      ✅ Visual status indicators (✅ ⚠️ ❌)")
        print("\n   Simple Endpoint:")
        print("      ⚠️  Long paragraph format")
        print("      ⚠️  Harder to scan quickly")
        print("      ⚠️  No structured tables")
        print("      ⚠️  Not optimized for executives")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n❌ Comparison failed: {str(e)}")


if __name__ == "__main__":
    print("\n🚀 Starting Executive Quality Check Tests\n")
    
    # Run main test
    success = test_executive_quality_check()
    
    # Run comparison if main test succeeded
    if success:
        test_comparison()
    
    print("\n✨ All tests completed!\n")


"""
Test script for the new simple quality check endpoint
"""
import requests
import json

# API configuration
BASE_URL = "http://localhost:8000"
SIMPLE_QUALITY_CHECK_URL = f"{BASE_URL}/api/v1/quality-check-simple"

# Sample generated ISO template for testing
SAMPLE_TEMPLATE = """
ISO 9001:2015 Quality System Record

Document Title: Calibration Procedure for Laser Measurement Device
Document Number: QSR-2024-001
Revision Number: 1.0
Effective Date: 2024-01-15
Department: Quality Assurance
Author: Maria Lopez
Purpose: To establish a standardized calibration procedure for laser measurement devices
Scope: This procedure applies to all laser measurement devices used in the quality control laboratory

1. INTRODUCTION
This document outlines the calibration procedure for laser measurement devices in accordance with ISO 9001:2015 quality management standards.

2. RESPONSIBILITIES
The Quality Assurance department is responsible for ensuring all laser measurement devices are calibrated according to this procedure.

3. PROCEDURE
3.1 Calibration shall be performed annually
3.2 Only certified technicians may perform calibrations
3.3 Calibration records shall be maintained for a minimum of 5 years

4. RECORDS
All calibration activities shall be documented in the device log and maintained in the quality management system.
"""


def test_simple_quality_check():
    """Test the simple quality check endpoint"""
    print("Testing Simple Quality Check Endpoint")
    print("=" * 60)
    
    # Prepare the request
    payload = {
        "generated_template": SAMPLE_TEMPLATE
    }
    
    try:
        print("\nSending request to:", SIMPLE_QUALITY_CHECK_URL)
        print(f"Template length: {len(SAMPLE_TEMPLATE)} characters")
        print("-" * 60)
        
        # Make the request
        response = requests.post(
            SIMPLE_QUALITY_CHECK_URL,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # Check response status
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ SUCCESS!")
            print("=" * 60)
            print("\nQuality Report:")
            print("-" * 60)
            print(result.get("quality_report", "No report generated"))
            print("-" * 60)
            print(f"\nTimestamp: {result.get('timestamp')}")
            print(f"Success: {result.get('success')}")
        else:
            print(f"\n❌ ERROR!")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the API.")
        print("Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")


def test_with_empty_template():
    """Test with empty template (should fail)"""
    print("\n\nTesting with Empty Template (Expected to Fail)")
    print("=" * 60)
    
    payload = {
        "generated_template": ""
    }
    
    try:
        response = requests.post(
            SIMPLE_QUALITY_CHECK_URL,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ Correctly rejected empty template")
            print(f"Error message: {response.json().get('detail')}")
        else:
            print(f"Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("SIMPLE QUALITY CHECK ENDPOINT TEST")
    print("=" * 60)
    
    # Test 1: Valid template
    test_simple_quality_check()
    
    # Test 2: Empty template (should fail)
    test_with_empty_template()
    
    print("\n" + "=" * 60)
    print("TESTS COMPLETED")
    print("=" * 60 + "\n")


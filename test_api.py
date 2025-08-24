#!/usr/bin/env python3
"""
IntelliClaim API Test Script
Tests all endpoints and functionality
"""

import requests
import json
import time
from typing import Dict, Any

class IntelliClaimAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_health(self) -> bool:
        """Test health endpoint"""
        print("🔍 Testing Health Endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✅ Health check passed")
                print(f"   Response: {response.json()}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_gemini(self) -> bool:
        """Test Gemini API connectivity"""
        print("\n🔍 Testing Gemini API...")
        try:
            response = self.session.get(f"{self.base_url}/test-gemini")
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    print("✅ Gemini API working")
                    print(f"   Response: {result.get('response', '')[:100]}...")
                    return True
                else:
                    print(f"❌ Gemini API error: {result.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"❌ Gemini test failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Gemini test error: {e}")
            return False
    
    def test_query(self, query: str, expected_decision: str = None) -> bool:
        """Test query endpoint"""
        print(f"\n🔍 Testing Query: '{query}'")
        try:
            payload = {"query": query}
            response = self.session.post(
                f"{self.base_url}/query",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Query processed successfully")
                print(f"   Decision: {result.get('decision')}")
                print(f"   Justification: {result.get('justification')}")
                print(f"   Confidence: {result.get('confidence_score')}%")
                print(f"   Processing Time: {result.get('processing_time')}s")
                
                if expected_decision and result.get('decision') == expected_decision:
                    print(f"✅ Expected decision '{expected_decision}' matched")
                elif expected_decision:
                    print(f"⚠️  Expected '{expected_decision}' but got '{result.get('decision')}'")
                
                return True
            else:
                print(f"❌ Query failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Query error: {e}")
            return False
    
    def test_document_upload(self, file_path: str) -> bool:
        """Test document upload endpoint"""
        print(f"\n🔍 Testing Document Upload: {file_path}")
        try:
            with open(file_path, 'rb') as file:
                files = {'file': file}
                response = self.session.post(f"{self.base_url}/upload-document", files=files)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Document uploaded successfully")
                print(f"   Documents added: {result.get('documents_added')}")
                print(f"   File: {result.get('file')}")
                return True
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Upload error: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run all tests"""
        print("🚀 Starting IntelliClaim API Comprehensive Test")
        print("=" * 50)
        
        # Test 1: Health Check
        health_ok = self.test_health()
        if not health_ok:
            print("❌ Health check failed. Is the server running?")
            return
        
        # Test 2: Gemini API
        gemini_ok = self.test_gemini()
        
        # Test 3: Query Tests
        test_queries = [
            {
                "query": "46-year-old male, knee surgery in Pune, 3-month-old insurance policy",
                "expected": "REJECTED"
            },
            {
                "query": "25M, dental treatment, Chennai, new policy",
                "expected": "APPROVED"
            },
            {
                "query": "60-year-old woman, cataract surgery, Delhi, 5-year-old policy",
                "expected": "APPROVED"
            },
            {
                "query": "Female, 35 years, heart surgery, Mumbai, 1-year policy",
                "expected": "APPROVED"
            }
        ]
        
        query_results = []
        for test in test_queries:
            success = self.test_query(test["query"], test["expected"])
            query_results.append(success)
        
        # Test 4: Document Upload (if file exists)
        upload_ok = False
        try:
            # Try to upload a sample PDF if it exists
            upload_ok = self.test_document_upload("./sample_policy.pdf")
        except FileNotFoundError:
            print("\n⚠️  No sample PDF found. Skipping upload test.")
            print("   Create a sample_policy.pdf file to test upload functionality.")
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
        print(f"Gemini API: {'✅ PASS' if gemini_ok else '❌ FAIL'}")
        print(f"Query Tests: {sum(query_results)}/{len(query_results)} PASS")
        print(f"Upload Test: {'✅ PASS' if upload_ok else '⚠️  SKIP'}")
        
        if all([health_ok, gemini_ok, all(query_results)]):
            print("\n🎉 All critical tests passed! Your API is working correctly.")
        else:
            print("\n⚠️  Some tests failed. Check the errors above.")

def create_sample_policy():
    """Create a sample policy document for testing"""
    sample_content = """
    INSURANCE POLICY TERMS AND CONDITIONS
    
    WAITING PERIODS:
    - Minor procedures: No waiting period
    - Major procedures (surgery, heart procedures): 3-month waiting period
    - Pre-existing conditions: 12-month waiting period
    
    COVERAGE AMOUNTS:
    - Minor procedures: Up to ₹5,000
    - Major procedures: Up to ₹15,000
    - Senior citizens (60+): Up to ₹20,000
    
    EXCLUSIONS:
    - Cosmetic procedures
    - Experimental treatments
    - Procedures outside network hospitals
    
    NETWORK HOSPITALS:
    - Pune: City Hospital, Medical Center
    - Mumbai: General Hospital, Specialty Clinic
    - Delhi: Central Medical, Health Care
    - Chennai: Regional Hospital, Care Center
    """
    
    try:
        with open("sample_policy.pdf", "w") as f:
            f.write(sample_content)
        print("📄 Created sample_policy.txt (PDF simulation)")
        return True
    except Exception as e:
        print(f"❌ Could not create sample file: {e}")
        return False

if __name__ == "__main__":
    # Create sample policy if it doesn't exist
    create_sample_policy()
    
    # Run tests
    tester = IntelliClaimAPITester()
    tester.run_comprehensive_test() 
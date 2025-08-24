#!/usr/bin/env python3
"""
Comprehensive testing script for IntelliClaim system
"""

import asyncio
import json
import requests
import time
from typing import Dict, List

class IntelliClaimTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
    
    def test_health_check(self) -> bool:
        """Test health check endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, f"Status: {data.get('status')}")
                return True
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Error: {str(e)}")
            return False
    
    def test_gemini_connection(self) -> bool:
        """Test Gemini API connection"""
        try:
            response = requests.get(f"{self.base_url}/test-gemini")
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    self.log_test("Gemini Connection", True, "API connection successful")
                    return True
                else:
                    self.log_test("Gemini Connection", False, f"API error: {data.get('error')}")
                    return False
            else:
                self.log_test("Gemini Connection", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Gemini Connection", False, f"Error: {str(e)}")
            return False
    
    def test_system_stats(self) -> bool:
        """Test system statistics endpoint"""
        try:
            response = requests.get(f"{self.base_url}/system-stats")
            if response.status_code == 200:
                data = response.json()
                self.log_test("System Stats", True, f"Documents: {data.get('total_documents')}")
                return True
            else:
                self.log_test("System Stats", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("System Stats", False, f"Error: {str(e)}")
            return False
    
    def test_document_listing(self) -> bool:
        """Test document listing endpoint"""
        try:
            response = requests.get(f"{self.base_url}/documents")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Document Listing", True, f"Found {data.get('total_documents')} documents")
                return True
            else:
                self.log_test("Document Listing", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Document Listing", False, f"Error: {str(e)}")
            return False
    
    def test_query_processing(self, test_queries: List[str]) -> bool:
        """Test query processing with sample queries"""
        success_count = 0
        for i, query in enumerate(test_queries):
            try:
                response = requests.post(
                    f"{self.base_url}/query",
                    json={"query": query},
                    timeout=30
                )
                if response.status_code == 200:
                    data = response.json()
                    decision = data.get('decision', 'UNKNOWN')
                    confidence = data.get('confidence_score', 0)
                    self.log_test(f"Query {i+1}", True, f"Decision: {decision}, Confidence: {confidence}%")
                    success_count += 1
                else:
                    self.log_test(f"Query {i+1}", False, f"Status code: {response.status_code}")
            except Exception as e:
                self.log_test(f"Query {i+1}", False, f"Error: {str(e)}")
        
        return success_count == len(test_queries)
    
    def test_file_upload(self, file_path: str) -> bool:
        """Test file upload functionality"""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{self.base_url}/upload-document", files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test("File Upload", True, f"Uploaded {data.get('documents_added')} documents")
                    return True
                else:
                    self.log_test("File Upload", False, f"Status code: {response.status_code}")
                    return False
        except Exception as e:
            self.log_test("File Upload", False, f"Error: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run all tests"""
        print("🚀 Starting IntelliClaim System Tests\n")
        
        # Basic connectivity tests
        self.test_health_check()
        self.test_gemini_connection()
        self.test_system_stats()
        self.test_document_listing()
        
        # Test file upload if sample file exists
        sample_file = "sample_policy.pdf"
        if self.test_file_upload(sample_file):
            # Test queries after upload
            test_queries = [
                "46-year-old male, knee surgery in Pune, 3-month-old insurance policy",
                "Female, 35 years, heart surgery, Mumbai, 1-year policy",
                "25M, dental treatment, Chennai, new policy"
            ]
            self.test_query_processing(test_queries)
        
        # Print summary
        print(f"\n📊 Test Summary:")
        print(f"Total Tests: {len(self.test_results)}")
        passed = sum(1 for result in self.test_results if result['success'])
        failed = len(self.test_results) - passed
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/len(self.test_results)*100):.1f}%")
        
        # Save results
        with open("test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        return failed == 0

def main():
    """Main test runner"""
    tester = IntelliClaimTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 All tests passed! System is ready for use.")
    else:
        print("\n⚠️  Some tests failed. Please check the system configuration.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 
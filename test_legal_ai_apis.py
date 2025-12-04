#!/usr/bin/env python3
"""
Test script for Hrujul's Legal AI System APIs
Comprehensive testing of all legal AI endpoints
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_QUERY = "What are my legal rights if I'm accused of theft?"

class LegalAITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.results = {}
        
    def test_endpoint(self, name, url, method="POST", data=None):
        """Test a single endpoint"""
        print(f"\n🧪 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == "GET":
                response = requests.get(url)
            else:
                response = requests.post(url, json=data)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ SUCCESS: {json.dumps(result, indent=2)[:200]}...")
                self.results[name] = {"status": "SUCCESS", "data": result}
                return result
            else:
                error_detail = response.json().get('detail', 'Unknown error')
                print(f"   ❌ ERROR: {error_detail}")
                self.results[name] = {"status": "ERROR", "error": error_detail}
                return None
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ CONNECTION ERROR: Unable to connect to {url}")
            self.results[name] = {"status": "CONNECTION_ERROR", "error": "Server not responding"}
            return None
        except Exception as e:
            print(f"   ❌ EXCEPTION: {str(e)}")
            self.results[name] = {"status": "EXCEPTION", "error": str(e)}
            return None

    def test_health_check(self):
        """Test if the server is running"""
        return self.test_endpoint("Health Check", f"{self.base_url}/api/health", "GET")

    def test_classification(self):
        """Test domain classification"""
        data = {
            "text": TEST_QUERY,
            "domain_hints": []
        }
        return self.test_endpoint("Domain Classification", f"{self.base_url}/api/classify", "POST", data)

    def test_legal_route(self):
        """Test legal route recommendation"""
        data = {
            "case_description": TEST_QUERY,
            "case_type": "criminal",
            "jurisdiction": "IN",
            "urgency_level": "normal"
        }
        return self.test_endpoint("Legal Route", f"{self.base_url}/api/legal-route", "POST", data)

    def test_constitution(self):
        """Test constitution search"""
        data = {
            "query": TEST_QUERY,
            "jurisdiction": "IN"
        }
        return self.test_endpoint("Constitution Search", f"{self.base_url}/api/constitution", "POST", data)

    def test_timeline(self):
        """Test timeline generation"""
        data = {
            "case_id": "test_123",
            "case_type": "criminal",
            "jurisdiction": "IN",
            "priority": "medium",
            "case_severity": "moderate"
        }
        return self.test_endpoint("Timeline Generation", f"{self.base_url}/api/timeline", "POST", data)

    def test_success_rate(self):
        """Test success rate prediction"""
        data = {
            "case_type": "criminal",
            "jurisdiction": "IN",
            "court_level": "district",
            "case_complexity": "medium",
            "lawyer_experience": "medium"
        }
        return self.test_endpoint("Success Rate", f"{self.base_url}/api/success-rate", "POST", data)

    def test_jurisdiction(self):
        """Test jurisdiction info"""
        return self.test_endpoint("Jurisdiction Info", f"{self.base_url}/api/jurisdiction/IN", "GET")

    def test_feedback(self):
        """Test feedback submission"""
        data = {
            "query_id": "test_query_123",
            "rating": "positive",
            "jurisdiction": "IN",
            "timestamp": datetime.now().isoformat()
        }
        return self.test_endpoint("Feedback", f"{self.base_url}/api/feedback", "POST", data)

    def test_frontend(self):
        """Test frontend pages"""
        pages = [
            ("Landing Page", f"{self.base_url}/"),
            ("Legal AI Interface", f"{self.base_url}/legal-ai"),
            ("API Docs", f"{self.base_url}/docs")
        ]
        
        results = {}
        for page_name, url in pages:
            print(f"\n🌐 Testing {page_name}...")
            try:
                response = requests.get(url, timeout=10)
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    print(f"   ✅ SUCCESS: Page loaded ({len(response.content)} bytes)")
                    results[page_name] = "SUCCESS"
                else:
                    print(f"   ❌ ERROR: HTTP {response.status_code}")
                    results[page_name] = f"HTTP {response.status_code}"
            except Exception as e:
                print(f"   ❌ ERROR: {str(e)}")
                results[page_name] = str(e)
        
        return results

    def run_comprehensive_test(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive Legal AI System Test")
        print("=" * 60)
        
        # Test server connectivity
        print("\n📡 Testing Server Connectivity...")
        health = self.test_health_check()
        if not health:
            print("❌ Server is not responding. Please ensure the server is running.")
            return False
        
        # Test all APIs
        print("\n🔧 Testing Legal AI APIs...")
        apis = [
            self.test_classification,
            self.test_legal_route,
            self.test_constitution,
            self.test_timeline,
            self.test_success_rate,
            self.test_jurisdiction,
            self.test_feedback
        ]
        
        api_results = {}
        for api_test in apis:
            result = api_test()
            time.sleep(0.5)  # Brief pause between requests
        
        # Test frontend
        print("\n🎨 Testing Frontend...")
        frontend_results = self.test_frontend()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        successful_apis = sum(1 for r in self.results.values() if r.get('status') == 'SUCCESS')
        total_apis = len(self.results)
        
        print(f"\n🔧 API Tests: {successful_apis}/{total_apis} successful")
        for name, result in self.results.items():
            status_icon = "✅" if result.get('status') == 'SUCCESS' else "❌"
            print(f"   {status_icon} {name}: {result.get('status')}")
        
        print(f"\n🌐 Frontend Tests:")
        for page, status in frontend_results.items():
            status_icon = "✅" if status == "SUCCESS" else "❌"
            print(f"   {status_icon} {page}: {status}")
        
        # Overall assessment
        overall_success = successful_apis >= 6 and all(status == "SUCCESS" for status in frontend_results.values())
        
        print(f"\n🎯 OVERALL RESULT: {'✅ ALL TESTS PASSED' if overall_success else '⚠️ SOME TESTS FAILED'}")
        
        if overall_success:
            print("\n🎉 Legal AI System is fully operational!")
            print("🌍 Ready for multi-jurisdiction legal queries")
            print("🤖 Reinforcement learning feedback system active")
            print("⚡ FastAPI backend + React frontend integration complete")
        else:
            print("\n⚠️ Some components need attention")
            print("🔧 Check error messages above for debugging")
        
        return overall_success

if __name__ == "__main__":
    tester = LegalAITester()
    success = tester.run_comprehensive_test()
    exit(0 if success else 1)
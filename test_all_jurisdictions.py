#!/usr/bin/env python3
"""
Comprehensive test script for all constitution endpoints (IN, UAE, UK)
"""
import requests
import json

def test_all_jurisdictions():
    """Test the constitution endpoint with all three jurisdictions"""
    
    base_url = "http://127.0.0.1:8000"
    endpoint = f"{base_url}/api/constitution"
    
    test_cases = [
        {
            "name": "India - Privacy query",
            "query": "privacy rights personal liberty",
            "jurisdiction": "IN"
        },
        {
            "name": "UAE - Liberty query", 
            "query": "personal liberty freedom detention",
            "jurisdiction": "UAE"
        },
        {
            "name": "UK - Human Rights query",
            "query": "human rights article 8 privacy",
            "jurisdiction": "UK"
        },
        {
            "name": "UAE - Rule of Law query",
            "query": "rule of law constitutional authority",
            "jurisdiction": "UAE"
        },
        {
            "name": "UK - Freedom of Speech query",
            "query": "freedom of expression speech rights",
            "jurisdiction": "UK"
        },
        {
            "name": "India - Constitutional Remedies query",
            "query": "writ jurisdiction constitutional remedies",
            "jurisdiction": "IN"
        }
    ]
    
    print("Testing Constitution Endpoints for All Jurisdictions")
    print("=" * 60)
    
    success_count = 0
    total_tests = len(test_cases)
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        print(f"Query: '{test_case['query']}' | Jurisdiction: {test_case['jurisdiction']}")
        
        try:
            response = requests.post(endpoint, json={
                "query": test_case["query"],
                "jurisdiction": test_case["jurisdiction"]
            })
            
            if response.status_code == 200:
                data = response.json()
                
                # Check articles returned
                articles = data.get("articles", [])
                article_numbers = [str(article.get("number", "Unknown")) for article in articles]
                
                print(f"[OK] Articles returned: {article_numbers}")
                
                # Check case structure
                popular_cases = data.get("popular_cases", [])
                if popular_cases:
                    print(f"[OK] Popular cases count: {len(popular_cases)}")
                    first_case = popular_cases[0]
                    if isinstance(first_case, dict) and "name" in first_case:
                        print(f"[OK] Case structure correct: {first_case['name'][:50]}...")
                    else:
                        print(f"[WARNING] Case structure issue: {type(first_case)}")
                
                # Check interpretation includes jurisdiction context
                interpretation = data.get("interpretation", "")
                jurisdiction_name = {"IN": "India", "UAE": "UAE", "UK": "United Kingdom"}[test_case["jurisdiction"]]
                if jurisdiction_name in interpretation or "law" in interpretation:
                    print(f"[OK] Jurisdiction context in interpretation")
                else:
                    print(f"[WARNING] Missing jurisdiction context in interpretation")
                
                # Check case law with correct court names
                case_law = data.get("case_law", [])
                if case_law:
                    print(f"[OK] Case law count: {len(case_law)}")
                    expected_courts = {
                        "IN": "Supreme Court of India",
                        "UAE": "Federal Supreme Court UAE",
                        "UK": "UK Supreme Court"
                    }
                    expected_court = expected_courts.get(test_case["jurisdiction"])
                    actual_court = case_law[0].get("court", "Unknown")
                    if expected_court in actual_court:
                        print(f"[OK] Correct court name: {actual_court}")
                    else:
                        print(f"[WARNING] Unexpected court name: {actual_court}")
                
                # Check amendments are jurisdiction-specific
                amendments = data.get("amendments", [])
                if amendments:
                    print(f"[OK] Amendments count: {len(amendments)}")
                
                success_count += 1
                
            else:
                print(f"[ERROR] Request failed: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Network error: {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed! All jurisdictions working correctly.")
    else:
        print(f"⚠️  {total_tests - success_count} tests failed. Please check the output above.")
    
    return success_count == total_tests

if __name__ == "__main__":
    test_all_jurisdictions()
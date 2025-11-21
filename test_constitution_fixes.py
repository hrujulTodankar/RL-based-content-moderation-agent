#!/usr/bin/env python3
"""
Test script to validate the constitution endpoint fixes
"""
import requests
import json

def test_constitution_endpoint():
    """Test the constitution endpoint with different queries"""
    
    base_url = "http://127.0.0.1:8000"
    endpoint = f"{base_url}/api/constitution"
    
    test_cases = [
        {
            "name": "Religion query",
            "query": "religious freedom temple rights",
            "jurisdiction": "IN"
        },
        {
            "name": "Remedies query", 
            "query": "constitutional remedies writ jurisdiction",
            "jurisdiction": "IN"
        },
        {
            "name": "Liberty query",
            "query": "personal liberty privacy rights",
            "jurisdiction": "IN"
        },
        {
            "name": "General query",
            "query": "constitutional law legal rights",
            "jurisdiction": "IN"
        }
    ]
    
    print("Testing Constitution Endpoint Fixes")
    print("=" * 50)
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        print(f"Query: '{test_case['query']}'")
        
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
                
                # Check if we have diverse articles (not just 14, 19)
                unique_articles = set(article_numbers)
                if len(unique_articles) > 2:
                    print(f"[OK] Good diversity in articles: {len(unique_articles)} unique articles")
                elif len(unique_articles) == 2 and ("14" in unique_articles and "19" in unique_articles):
                    print(f"[WARNING] Still only returning articles 14 and 19")
                else:
                    print(f"[OK] Articles include: {', '.join(sorted(unique_articles))}")
                
                # Check popular cases structure
                popular_cases = data.get("popular_cases", [])
                if popular_cases:
                    print(f"[OK] Popular cases count: {len(popular_cases)}")
                    # Check first case structure
                    first_case = popular_cases[0]
                    if isinstance(first_case, dict) and "name" in first_case:
                        print(f"[OK] Case structure correct: {first_case['name'][:50]}...")
                    else:
                        print(f"[WARNING] Case structure issue: {type(first_case)}")
                
                # Check case_law structure
                case_law = data.get("case_law", [])
                if case_law:
                    print(f"[OK] Case law count: {len(case_law)}")
                    first_case_law = case_law[0]
                    if isinstance(first_case_law, dict) and "case" in first_case_law:
                        print(f"[OK] Case law structure correct: {first_case_law['case'][:50]}...")
                    else:
                        print(f"[WARNING] Case law structure issue: {type(first_case_law)}")
                        
            else:
                print(f"[ERROR] Request failed: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Network error: {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed. Check the output above for any issues.")

if __name__ == "__main__":
    test_constitution_endpoint()
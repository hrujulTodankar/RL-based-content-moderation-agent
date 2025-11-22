#!/usr/bin/env python3
"""
Test script to verify precise article relevance filtering
"""
import requests
import json

def test_precise_relevance():
    """Test that constitution endpoint only returns highly relevant articles"""
    
    base_url = "http://127.0.0.1:8000"
    endpoint = f"{base_url}/api/constitution"
    
    test_cases = [
        # Should return specific relevant articles
        {
            "name": "UAE - Specific Economic Rights",
            "query": "economic rights social security employment",
            "jurisdiction": "UAE",
            "expected_articles": [20]  # Should focus on Article 20
        },
        {
            "name": "UAE - Women's Rights Specific",
            "query": "women gender equality workplace leadership",
            "jurisdiction": "UAE", 
            "expected_articles": [40]  # Should focus on Article 40
        },
        {
            "name": "UK - Fair Trial Specific",
            "query": "fair trial independent tribunal hearing",
            "jurisdiction": "UK",
            "expected_articles": [6]  # Should focus on Article 6
        },
        {
            "name": "UK - Property Rights Specific", 
            "query": "property rights peaceful enjoyment compensation",
            "jurisdiction": "UK",
            "expected_articles": ["P1-1"]  # Should focus on Protocol 1, Article 1
        },
        # Vague queries should return fewer articles
        {
            "name": "UAE - Vague Query",
            "query": "rights",
            "jurisdiction": "UAE",
            "expected_articles": None  # Should return very few or none
        },
        {
            "name": "UK - Vague Query",
            "query": "freedom",
            "jurisdiction": "UK", 
            "expected_articles": None  # Should return very few or none
        }
    ]
    
    print("Testing Precise Article Relevance Filtering")
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
                print(f"[OK] Article count: {len(articles)}")
                
                # For specific queries, check if we got expected articles
                if test_case["expected_articles"]:
                    expected_strs = [str(x) for x in test_case["expected_articles"]]
                    if any(exp in article_numbers for exp in expected_strs):
                        print(f"[OK] Found expected article(s): {expected_strs}")
                        success_count += 1
                    else:
                        print(f"[WARNING] Expected articles {expected_strs} not found")
                else:
                    # For vague queries, expect fewer articles
                    if len(articles) <= 2:
                        print(f"[OK] Vague query returned minimal articles (as expected)")
                        success_count += 1
                    else:
                        print(f"[WARNING] Vague query returned {len(articles)} articles (expected ≤2)")
                
                # Check interpretation quality
                interpretation = data.get("interpretation", "")
                if "particularly relevant" in interpretation:
                    print(f"[OK] Interpretation mentions relevance")
                else:
                    print(f"[INFO] Interpretation: {interpretation[:100]}...")
                
            else:
                print(f"[ERROR] Request failed: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Network error: {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {success_count}/{total_tests} tests passed")
    
    if success_count >= total_tests * 0.8:  # 80% success rate
        print("Success! Precise relevance filtering is working correctly.")
        return True
    else:
        print(f"Warning: Only {success_count}/{total_tests} tests passed.")
        return False

if __name__ == "__main__":
    test_precise_relevance()
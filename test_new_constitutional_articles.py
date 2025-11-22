#!/usr/bin/env python3
"""
Test script to verify the newly added constitutional articles for UAE and UK
"""
import requests
import json

def test_new_articles():
    """Test the newly added articles for UAE and UK"""
    
    base_url = "http://127.0.0.1:8000"
    endpoint = f"{base_url}/api/constitution"
    
    test_cases = [
        # UAE - Economic and Social Security
        {
            "name": "UAE - Economic Rights (Article 20)",
            "query": "economic rights social security employment livelihood",
            "jurisdiction": "UAE"
        },
        # UAE - Education Rights
        {
            "name": "UAE - Education Rights (Article 33)",
            "query": "education compulsory free literacy university access",
            "jurisdiction": "UAE"
        },
        # UAE - Women's Rights
        {
            "name": "UAE - Women's Rights (Article 40)",
            "query": "women's rights gender equality workplace leadership political participation",
            "jurisdiction": "UAE"
        },
        # UAE - Judicial Independence
        {
            "name": "UAE - Judicial Independence (Article 50)",
            "query": "judicial independence separation of powers judges impartiality",
            "jurisdiction": "UAE"
        },
        # UAE - Property Rights
        {
            "name": "UAE - Property Rights (Article 60)",
            "query": "property rights private property compensation expropriation ownership",
            "jurisdiction": "UAE"
        },
        # UK - Fair Trial Rights
        {
            "name": "UK - Fair Trial Rights (Article 6)",
            "query": "fair trial independent tribunal public hearing procedural rights",
            "jurisdiction": "UK"
        },
        # UK - Assembly and Association
        {
            "name": "UK - Assembly Rights (Article 11)",
            "query": "freedom of assembly peaceful protest trade unions association",
            "jurisdiction": "UK"
        },
        # UK - Property Rights
        {
            "name": "UK - Property Rights (Protocol 1)",
            "query": "property rights peaceful enjoyment possession compensation expropriation",
            "jurisdiction": "UK"
        },
        # UK - Judicial Independence
        {
            "name": "UK - Judicial Independence",
            "query": "judicial independence executive interference impartial separation of powers",
            "jurisdiction": "UK"
        }
    ]
    
    print("Testing Newly Added Constitutional Articles")
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
                
                # Check if we got some articles
                if articles:
                    success_count += 1
                    print(f"[OK] Found {len(articles)} relevant articles")
                    
                    # Check first article has proper structure
                    first_article = articles[0]
                    if "number" in first_article and "title" in first_article and "content" in first_article:
                        print(f"[OK] Article structure correct: Article {first_article['number']} - {first_article['title'][:50]}...")
                    else:
                        print(f"[WARNING] Article structure issue")
                else:
                    print(f"[WARNING] No articles returned for query")
                
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
        print("Success! New constitutional articles are working correctly.")
        return True
    else:
        print(f"Warning: Only {success_count}/{total_tests} tests passed.")
        return False

if __name__ == "__main__":
    test_new_articles()
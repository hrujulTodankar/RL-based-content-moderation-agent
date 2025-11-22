#!/usr/bin/env python3
"""
Quick manual test for UK property rights
"""
import requests
import json

def test_uk_property():
    url = "http://127.0.0.1:8000/api/constitution"
    
    # Test property rights query
    data = {
        "query": "property rights peaceful enjoyment compensation",
        "jurisdiction": "UK"
    }
    
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        articles = result.get("articles", [])
        print(f"Articles found: {[str(a['number']) for a in articles]}")
        
        for article in articles:
            print(f"  Article {article['number']}: {article['title']}")
            
        print(f"Query analysis: {result.get('query_analysis', {})}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_uk_property()
#!/usr/bin/env python3
"""
Debug script to test constitution endpoint directly
"""
import sys
import traceback
import asyncio
from app.endpoints.constitution import search_constitution, ConstitutionRequest

async def test_constitution_debug():
    """Test constitution endpoint with detailed error reporting"""
    
    test_cases = [
        {
            "name": "UAE - Economic Rights",
            "request": ConstitutionRequest(
                query="economic rights social security employment livelihood",
                jurisdiction="UAE"
            )
        },
        {
            "name": "UAE - Women's Rights",
            "request": ConstitutionRequest(
                query="women's rights gender equality workplace leadership",
                jurisdiction="UAE"
            )
        },
        {
            "name": "UK - Fair Trial",
            "request": ConstitutionRequest(
                query="fair trial independent tribunal public hearing",
                jurisdiction="UK"
            )
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{'='*50}")
        print(f"Testing: {test_case['name']}")
        print(f"Query: '{test_case['request'].query}'")
        print(f"Jurisdiction: {test_case['request'].jurisdiction}")
        print('-'*50)
        
        try:
            result = await search_constitution(test_case['request'])
            print(f"[SUCCESS] Found {len(result.articles)} articles")
            for article in result.articles:
                print(f"  Article {article['number']}: {article['title']}")
        except Exception as e:
            print(f"[ERROR] Exception occurred: {type(e).__name__}")
            print(f"[ERROR] Message: {str(e)}")
            print(f"[ERROR] Traceback:")
            traceback.print_exc()
            print("-"*50)

if __name__ == "__main__":
    asyncio.run(test_constitution_debug())
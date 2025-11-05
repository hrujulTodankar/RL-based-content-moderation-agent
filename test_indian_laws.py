#!/usr/bin/env python3
"""
Test script for Indian Laws moderation using the RL-powered API
"""

import requests
import json
import time
from indian_laws_data import get_sample_content_for_testing, get_all_laws

API_BASE_URL = "http://localhost:8000/api"

def test_moderation_api():
    """Test the moderation API with Indian laws content"""

    print("Testing RL-Powered Content Moderation API with Indian Laws Data")
    print("=" * 70)

    # Test with sample content
    sample_data = get_sample_content_for_testing()

    print(f"\nTesting with {len(sample_data)} sample cases:\n")

    results = []

    for category, subcategory, content in sample_data:
        print(f"Testing: {category} - {subcategory}")
        print(f"   Content: {content[:50]}...")

        try:
            response = requests.post(
                f"{API_BASE_URL}/moderate",
                json={
                    "content": content,
                    "content_type": "text"
                },
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                result = response.json()
                print("   Moderated successfully")
                print(f"   Flagged: {result['flagged']}, Score: {result['score']:.3f}, Confidence: {result['confidence']:.3f}")
                print(f"   Reasons: {', '.join(result['reasons'])}")

                results.append({
                    "category": category,
                    "subcategory": subcategory,
                    "content": content,
                    "result": result
                })
            else:
                print(f"   API Error: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"   Request failed: {str(e)}")

        print()
        time.sleep(0.5)  # Brief pause between requests

    # Summary
    print("SUMMARY:")
    print("-" * 30)

    if results:
        flagged_count = sum(1 for r in results if r["result"]["flagged"])
        total_score = sum(r["result"]["score"] for r in results)
        avg_score = total_score / len(results)
        avg_confidence = sum(r["result"]["confidence"] for r in results) / len(results)

        print(f"Successfully moderated: {len(results)} cases")
        print(f"Flagged content: {flagged_count}")
        print(f"Average score: {avg_score:.3f}")
        print(f"Average confidence: {avg_confidence:.1f}%")
        # Category breakdown
        print("\nBy Category:")
        categories = {}
        for result in results:
            cat = result["category"]
            if cat not in categories:
                categories[cat] = {"total": 0, "flagged": 0}
            categories[cat]["total"] += 1
            if result["result"]["flagged"]:
                categories[cat]["flagged"] += 1

        for cat, stats in categories.items():
            print(f"   {cat}: {stats['flagged']}/{stats['total']} flagged")
    else:
        print("No successful moderations")

    print("\nNext Steps:")
    print("   1. Add more Indian laws data to indian_laws_data.py")
    print("   2. Test with different content types (images, documents)")
    print("   3. Provide feedback to improve the RL model")
    print("   4. Integrate with your website's content management system")

def test_with_full_laws():
    """Test with full Indian laws content"""

    print("\nTesting with full Indian laws content:\n")

    all_laws = get_all_laws()
    success_count = 0

    for law in all_laws:
        print(f"Testing: {law['act']} - {law['section']}")
        print(f"   Content: {law['content'][:60]}...")

        try:
            response = requests.post(
                f"{API_BASE_URL}/moderate",
                json={
                    "content": law["content"],
                    "content_type": "text",
                    "metadata": {
                        "law_category": law["category"],
                        "law_section": law["section"],
                        "act_name": law["act"]
                    }
                },
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                result = response.json()
                print("   Moderated")
                print(f"   Flagged: {result['flagged']}, Score: {result['score']:.3f}")
                success_count += 1
            else:
                print(f"   Error: {response.status_code}")

        except Exception as e:
            print(f"   Failed: {str(e)}")

        print()
        time.sleep(0.5)

    print(f"Full laws test: {success_count}/{len(all_laws)} successful")

if __name__ == "__main__":
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("API is running")
            test_moderation_api()
            # Uncomment to test with full laws (may take longer)
            # test_with_full_laws()
        else:
            print("API health check failed")
    except Exception as e:
        print(f"Cannot connect to API: {str(e)}")
        print("Make sure the server is running: python -m app.main")
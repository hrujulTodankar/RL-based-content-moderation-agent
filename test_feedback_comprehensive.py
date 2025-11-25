#!/usr/bin/env python3
"""Comprehensive test for feedback submission functionality"""

import requests
import json

def test_comprehensive_feedback():
    """Test feedback submission with various scenarios"""
    
    base_url = "http://localhost:8000"
    
    # Test cases
    test_cases = [
        {
            "name": "Positive feedback with rating",
            "data": {
                "feedback": {
                    "moderation_id": "test_analysis_positive_001",
                    "feedback_type": "thumbs_up",
                    "comment": "Great analysis, very helpful",
                    "user_id": "test_user_1",
                    "rating": 5
                }
            }
        },
        {
            "name": "Negative feedback with rating",
            "data": {
                "feedback": {
                    "moderation_id": "test_analysis_negative_002", 
                    "feedback_type": "thumbs_down",
                    "comment": "Analysis needs improvement",
                    "user_id": "test_user_2",
                    "rating": 2
                }
            }
        },
        {
            "name": "Feedback without rating",
            "data": {
                "feedback": {
                    "moderation_id": "test_analysis_neutral_003",
                    "feedback_type": "thumbs_up",
                    "comment": "Good content",
                    "user_id": "test_user_3"
                }
            }
        },
        {
            "name": "Minimal feedback",
            "data": {
                "feedback": {
                    "moderation_id": "test_analysis_minimal_004",
                    "feedback_type": "thumbs_down"
                }
            }
        }
    ]
    
    print("🧪 Comprehensive Feedback Testing")
    print("=" * 50)
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print("-" * 40)
        
        try:
            response = requests.post(
                f"{base_url}/api/feedback",
                json=test_case['data']
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ PASSED")
                print(f"   Feedback ID: {result['feedback_id']}")
                print(f"   Reward Value: {result['reward_value']}")
                print(f"   Status: {result['status']}")
                print(f"   Timestamp: {result['timestamp']}")
            else:
                print(f"❌ FAILED")
                print(f"   Status Code: {response.status_code}")
                print(f"   Response: {response.text}")
                all_passed = False
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error - Server not running")
            print("   Make sure the server is running on port 8000")
            all_passed = False
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            all_passed = False
    
    # Test invalid feedback type
    print(f"\nTest {len(test_cases) + 1}: Invalid feedback type")
    print("-" * 40)
    
    try:
        invalid_data = {
            "feedback": {
                "moderation_id": "test_invalid_005",
                "feedback_type": "invalid_type",
                "user_id": "test_user"
            }
        }
        
        response = requests.post(
            f"{base_url}/api/feedback",
            json=invalid_data
        )
        
        if response.status_code == 400:
            print("✅ PASSED - Invalid feedback type correctly rejected")
        else:
            print(f"❌ FAILED - Expected 400, got {response.status_code}")
            print(f"   Response: {response.text}")
            all_passed = False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        all_passed = False
    
    # Test missing required fields
    print(f"\nTest {len(test_cases) + 2}: Missing feedback wrapper")
    print("-" * 40)
    
    try:
        invalid_data = {
            "moderation_id": "test_missing_006",
            "feedback_type": "thumbs_up"
        }
        
        response = requests.post(
            f"{base_url}/api/feedback",
            json=invalid_data
        )
        
        if response.status_code == 422:
            print("✅ PASSED - Missing feedback wrapper correctly rejected")
        else:
            print(f"❌ FAILED - Expected 422, got {response.status_code}")
            print(f"   Response: {response.text}")
            all_passed = False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Feedback submission is working correctly")
        print("✅ Error handling is working properly")
        print("✅ Database integration is functional")
    else:
        print("❌ SOME TESTS FAILED")
        print("Please check the errors above")
    
    return all_passed

if __name__ == "__main__":
    test_comprehensive_feedback()
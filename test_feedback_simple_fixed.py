#!/usr/bin/env python3
"""Simple test for the feedback API endpoint"""

import requests
import json

def test_feedback_api():
    """Test the feedback API endpoint"""
    url = "http://localhost:8000/api/feedback"
    
    # Test data for feedback submission (wrapped in feedback object)
    test_data = {
        "feedback": {
            "moderation_id": "test_analysis_456",
            "feedback_type": "thumbs_down",
            "comment": "Analysis needs improvement",
            "user_id": "test_user",
            "rating": 2
        }
    }
    
    try:
        print("Testing feedback API...")
        response = requests.post(url, json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            print("Feedback API test PASSED")
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"Feedback API test FAILED")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("Connection error - make sure the server is running on port 8000")
        return False
    except Exception as e:
        print(f"Error testing feedback API: {e}")
        return False

if __name__ == "__main__":
    test_feedback_api()
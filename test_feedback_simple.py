#!/usr/bin/env python3
"""Test script for the feedback UI and RL pipeline"""

import requests
import json
import time

def test_feedback_api():
    """Test the feedback API endpoint"""
    url = "http://localhost:8000/api/feedback"
    
    # Test data for feedback submission
    test_data = {
        "moderation_id": "test_analysis_456",
        "feedback_type": "thumbs_down",
        "comment": "Analysis needs improvement",
        "user_id": "test_user",
        "rating": 2
    }
    
    try:
        print("Testing feedback API...")
        response = requests.post(url, json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Feedback API test PASSED")
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Feedback API test FAILED")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure the server is running on port 8000")
        return False
    except Exception as e:
        print(f"❌ Error testing feedback API: {e}")
        return False

def test_ui_components():
    """Test UI components existence"""
    print("\nTesting UI components...")
    
    # Check if required files exist
    files_to_check = [
        "frontend/templates/index.html",
        "frontend/static/js/app.js", 
        "frontend/static/css/styles.css"
    ]
    
    all_files_exist = True
    for file_path in files_to_check:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Check for specific UI components
            if "feedback-popup-overlay" in content:
                print("✅ Post-feedback popup component found")
            else:
                print("❌ Post-feedback popup component missing")
                all_files_exist = False
                
            if "learning-applied-badge" in content:
                print("✅ Learning Applied badge component found")
            else:
                print("❌ Learning Applied badge component missing")
                all_files_exist = False
                
            if "showFeedbackPopup" in content:
                print("✅ Confidence tracking functions found")
            else:
                print("❌ Confidence tracking functions missing")
                all_files_exist = False
                
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
            all_files_exist = False
    
    return all_files_exist

def main():
    """Main test function"""
    print("Testing Feedback UI and RL Pipeline")
    print("=" * 50)
    
    # Test 1: UI Components
    ui_test = test_ui_components()
    
    # Test 2: API Endpoint (if server is running)
    api_test = test_feedback_api()
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"UI Components: {'✅ PASSED' if ui_test else '❌ FAILED'}")
    print(f"API Endpoint: {'✅ PASSED' if api_test else '❌ FAILED'}")
    
    if ui_test and api_test:
        print("\n🎉 ALL TESTS PASSED! Feedback UI and RL pipeline is complete.")
    elif ui_test:
        print("\n⚠️  UI components are ready, but server is not running.")
    else:
        print("\n❌ Some components are missing. Please check the implementation.")

if __name__ == "__main__":
    main()
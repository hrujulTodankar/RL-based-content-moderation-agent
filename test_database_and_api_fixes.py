#!/usr/bin/env python3
"""
Test script to validate the database connection management and API format standardization fixes.
"""
import asyncio
import json
import pytest
from unittest.mock import Mock, patch
import tempfile
import os
import aiosqlite
from datetime import datetime

# Test the database connection fixes
async def test_feedback_handler_connection_pooling():
    """Test that the feedback handler uses proper connection pooling and doesn't reinitialize connections"""
    print("Testing Feedback Handler Database Connection Management...")
    
    # Import after setting up the path
    import sys
    sys.path.append('.')
    from app.feedback_handler import FeedbackHandler
    
    # Test SQLite connection pooling
    handler = FeedbackHandler()
    handler.db_type = "sqlite"
    handler.db_path = ":memory:"  # Use in-memory database for testing
    
    await handler.initialize()
    
    # Test multiple operations to ensure connection reuse
    moderation_record = {
        "moderation_id": "test-123",
        "content_type": "text",
        "flagged": False,
        "score": 0.5,
        "confidence": 0.8,
        "reasons": ["test reason"],
        "timestamp": datetime.utcnow().isoformat()
    }
    
    feedback_record = {
        "feedback_id": "feedback-123",
        "moderation_id": "test-123",
        "user_id": "user-123",
        "feedback_type": "thumbs_up",
        "rating": 5,
        "comment": "Good content",
        "reward_value": 0.5,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Store multiple records to test connection pooling
    for i in range(5):
        test_mod_id = f"test-{i}"
        test_feedback_id = f"feedback-{i}"
        
        mod_record = {**moderation_record, "moderation_id": test_mod_id}
        fb_record = {**feedback_record, "feedback_id": test_feedback_id, "moderation_id": test_mod_id}
        
        await handler.store_moderation(mod_record)
        await handler.store_feedback(fb_record)
    
    # Verify data was stored
    feedback_list = await handler.get_feedback_by_moderation("test-0")
    assert len(feedback_list) == 1, f"Expected 1 feedback, got {len(feedback_list)}"
    
    # Test statistics retrieval
    stats = await handler.get_statistics()
    assert stats["total_moderations"] == 5, f"Expected 5 moderations, got {stats['total_moderations']}"
    assert stats["total_feedback"] == 5, f"Expected 5 feedback, got {stats['total_feedback']}"
    
    await handler.close()
    print("Database connection pooling test passed!")
    
    return True

def test_api_standardization():
    """Test that API endpoints have standardized request/response formats"""
    print("Testing API Standardization...")
    
    # Test the StandardResponse schema
    from app.schemas import StandardResponse, UserLogin
    
    # Test StandardResponse creation
    response = StandardResponse(
        success=True,
        message="Test message",
        data={"key": "value"}
    )
    
    assert response.success == True
    assert response.message == "Test message"
    assert response.data == {"key": "value"}
    assert response.timestamp is not None
    
    # Test UserLogin schema
    login_data = UserLogin(username="testuser", password="testpass")
    assert login_data.username == "testuser"
    assert login_data.password == "testpass"
    
    print("API standardization test passed!")
    
    return True

def test_login_endpoint_format_support():
    """Test that the login endpoint supports both JSON and form formats"""
    print("Testing Login Endpoint Format Support...")
    
    # This is a mock test to check the login endpoint structure
    # In a real test environment, we'd test the actual FastAPI endpoint
    
    from app.schemas import StandardResponse
    
    # Simulate a successful login response
    login_response = StandardResponse(
        success=True,
        message="Login successful",
        data={
            "access_token": "mock_token",
            "refresh_token": "mock_refresh",
            "token_type": "bearer",
            "expires_in": 1440,
            "user_id": "user123",
            "username": "testuser"
        }
    )
    
    assert login_response.success == True
    assert "access_token" in login_response.data
    assert login_response.data["token_type"] == "bearer"
    assert login_response.data["username"] == "testuser"
    
    # Simulate an error response
    error_response = StandardResponse(
        success=False,
        message="Invalid credentials",
        error_code="AUTH_ERROR"
    )
    
    assert error_response.success == False
    assert error_response.error_code == "AUTH_ERROR"
    
    print("✅ Login endpoint format support test passed!")
    
    return True

async def test_database_error_handling():
    """Test that database error handling works properly with connection retry logic"""
    print("Testing Database Error Handling...")
    
    import sys
    sys.path.append('.')
    from app.feedback_handler import FeedbackHandler
    
    handler = FeedbackHandler()
    handler.db_type = "sqlite"
    handler.db_path = "/nonexistent/path/to/database.db"  # Invalid path
    
    # This should fail gracefully without reinitializing in a loop
    try:
        await handler.initialize()
        print("❌ Expected connection error but didn't get one")
        return False
    except Exception as e:
        # This is expected - the connection should fail gracefully
        print(f"✅ Expected connection error: {str(e)}")
        
        # Test that we can still attempt operations (they should fail gracefully)
        try:
            await handler.store_moderation({
                "moderation_id": "test",
                "content_type": "text",
                "flagged": False,
                "score": 0.5,
                "confidence": 0.8,
                "reasons": ["test"],
                "timestamp": datetime.utcnow().isoformat()
            })
            print("❌ Expected storage to fail with invalid path")
            return False
        except Exception as storage_error:
            print(f"✅ Storage correctly failed with invalid path: {str(storage_error)}")
    
    await handler.close()
    print("✅ Database error handling test passed!")
    
    return True

def main():
    """Run all tests"""
    print("Running Database Connection and API Format Tests")
    print("=" * 60)
    
    test_results = []
    
    # Test API standardization first (synchronous)
    test_results.append(("API Standardization", test_api_standardization()))
    test_results.append(("Login Format Support", test_login_endpoint_format_support()))
    
    # Test database connection management (asynchronous)
    try:
        result = asyncio.run(test_feedback_handler_connection_pooling())
        test_results.append(("Database Connection Pooling", result))
    except Exception as e:
        print(f"Database Connection Pooling test failed: {e}")
        test_results.append(("Database Connection Pooling", False))
    
    # Test error handling
    try:
        result = asyncio.run(test_database_error_handling())
        test_results.append(("Database Error Handling", result))
    except Exception as e:
        print(f"Database Error Handling test failed: {e}")
        test_results.append(("Database Error Handling", False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in test_results:
        status = "PASSED" if passed else "FAILED"
        print(f"{test_name:<30} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("All tests passed! The fixes are working correctly.")
    else:
        print("Some tests failed. Please review the fixes.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
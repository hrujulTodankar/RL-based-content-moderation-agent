#!/usr/bin/env python3
"""
Comprehensive tests for security middleware and utilities
"""

import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.security import (
    SecurityManager, RateLimiter, AuthRateLimiter,
    InputSanitizer, security_manager, api_rate_limiter,
    auth_rate_limiter, generate_secure_token, constant_time_compare
)
from app.main import app


class TestSecurityManager:
    """Test SecurityManager functionality"""

    def setup_method(self):
        """Setup test fixtures"""
        self.security_manager = SecurityManager()

    def test_get_client_ip_direct(self):
        """Test client IP extraction from direct connection"""
        mock_request = Mock()
        mock_request.client = Mock()
        mock_request.client.host = "192.168.1.100"
        mock_request.headers = {}

        ip = self.security_manager.get_client_ip(mock_request)
        assert ip == "192.168.1.100"

    def test_get_client_ip_x_forwarded_for(self):
        """Test client IP extraction from X-Forwarded-For header"""
        mock_request = Mock()
        mock_request.client = None
        mock_request.headers = {"X-Forwarded-For": "203.0.113.1, 198.51.100.1"}

        ip = self.security_manager.get_client_ip(mock_request)
        assert ip == "203.0.113.1"

    def test_get_client_ip_x_real_ip(self):
        """Test client IP extraction from X-Real-IP header"""
        mock_request = Mock()
        mock_request.client = None
        mock_request.headers = {"X-Real-IP": "203.0.113.2"}

        ip = self.security_manager.get_client_ip(mock_request)
        assert ip == "203.0.113.2"

    def test_get_client_ip_unknown(self):
        """Test fallback for unknown client IP"""
        mock_request = Mock()
        mock_request.client = None
        mock_request.headers = {}

        ip = self.security_manager.get_client_ip(mock_request)
        assert ip == "unknown"

    def test_validate_input_sanitization(self):
        """Test input validation and sanitization"""
        test_data = {
            "content": "Normal content",
            "email": "test@example.com",
            "content_type": "text",
            "filename": "test.jpg"
        }

        sanitized = self.security_manager.validate_input(test_data)

        assert sanitized["content"] == "Normal content"
        assert sanitized["email"] == "test@example.com"
        assert sanitized["content_type"] == "text"

    def test_validate_input_invalid_email(self):
        """Test invalid email rejection"""
        test_data = {"email": "invalid-email"}

        with pytest.raises(HTTPException) as exc_info:
            self.security_manager.validate_input(test_data)

        assert exc_info.value.status_code == 400
        assert "Invalid email format" in str(exc_info.value.detail)

    def test_validate_input_invalid_content_type(self):
        """Test invalid content type rejection"""
        test_data = {"content_type": "invalid_type"}

        with pytest.raises(HTTPException) as exc_info:
            self.security_manager.validate_input(test_data)

        assert exc_info.value.status_code == 400
        assert "Invalid content type" in str(exc_info.value.detail)


class TestRateLimiter:
    """Test RateLimiter functionality"""

    def setup_method(self):
        """Setup test fixtures"""
        self.limiter = RateLimiter()

    def test_rate_limit_allowed(self):
        """Test allowing requests within limit"""
        key = "test_client"

        # Should allow initial requests
        for i in range(10):
            assert self.limiter.is_allowed(key, 10, 60) == True

    def test_rate_limit_exceeded(self):
        """Test blocking requests over limit"""
        key = "test_client"

        # Use up all requests
        for i in range(10):
            self.limiter.is_allowed(key, 10, 60)

        # Next request should be blocked
        assert self.limiter.is_allowed(key, 10, 60) == False

    def test_rate_limit_window_reset(self):
        """Test rate limit window reset"""
        key = "test_client"

        # Use up requests
        for i in range(5):
            self.limiter.is_allowed(key, 5, 1)  # 1 second window

        # Should be blocked
        assert self.limiter.is_allowed(key, 5, 1) == False

        # Simulate time passing (clear the limiter)
        self.limiter.requests[key] = []

        # Should allow again
        assert self.limiter.is_allowed(key, 5, 1) == True


class TestAuthRateLimiter:
    """Test AuthRateLimiter functionality"""

    def setup_method(self):
        """Setup test fixtures"""
        self.limiter = AuthRateLimiter()

    def test_auth_rate_limit_success(self):
        """Test successful auth resets counter"""
        ip = "192.168.1.100"

        # Failed attempts
        result = self.limiter.record_attempt(ip, False)
        assert result["locked"] == False
        assert result["attempts_remaining"] == 4

        # Successful auth
        result = self.limiter.record_attempt(ip, True)
        assert result["locked"] == False
        assert result["attempts_remaining"] == 5

    def test_auth_rate_limit_lockout(self):
        """Test IP lockout after max attempts"""
        ip = "192.168.1.100"

        # Use up all attempts
        for i in range(5):
            result = self.limiter.record_attempt(ip, False)
            if i < 4:
                assert result["locked"] == False
            else:
                assert result["locked"] == True

        # Should remain locked
        assert self.limiter.is_locked(ip) == True

    def test_auth_rate_limit_lockout_expiry(self):
        """Test lockout expiry"""
        ip = "192.168.1.100"

        # Trigger lockout
        for i in range(5):
            self.limiter.record_attempt(ip, False)

        assert self.limiter.is_locked(ip) == True

        # Simulate lockout expiry by manually setting old time
        import time
        self.limiter.attempts[ip]["locked_until"] = time.time() - 100

        assert self.limiter.is_locked(ip) == False


class TestInputSanitizer:
    """Test InputSanitizer functionality"""

    def test_sanitize_string_normal(self):
        """Test normal string sanitization"""
        input_str = "Normal string"
        result = InputSanitizer.sanitize_string(input_str)
        assert result == "Normal string"

    def test_sanitize_string_null_bytes(self):
        """Test null byte removal"""
        input_str = "String\x00with\x00nulls"
        result = InputSanitizer.sanitize_string(input_str)
        assert "\x00" not in result

    def test_sanitize_string_control_chars(self):
        """Test control character removal"""
        input_str = "String\x01\x02\x03with\x7fcontrol"
        result = InputSanitizer.sanitize_string(input_str)
        # Should only contain printable chars, newlines, tabs
        assert all(ord(c) >= 32 or c in '\n\t\r' for c in result)

    def test_sanitize_string_truncation(self):
        """Test string truncation"""
        long_string = "a" * 10000
        result = InputSanitizer.sanitize_string(long_string, max_length=100)
        assert len(result) == 100

    def test_sanitize_filename_normal(self):
        """Test normal filename sanitization"""
        filename = "test_file.jpg"
        result = InputSanitizer.sanitize_filename(filename)
        assert result == "test_file.jpg"

    def test_sanitize_filename_path_traversal(self):
        """Test path traversal removal"""
        filename = "../../../etc/passwd"
        result = InputSanitizer.sanitize_filename(filename)
        assert ".." not in result
        assert "/" not in result

    def test_sanitize_filename_special_chars(self):
        """Test special character removal"""
        filename = "test<file>.jpg"
        result = InputSanitizer.sanitize_filename(filename)
        assert "<" not in result
        assert ">" not in result

    def test_validate_filename_too_long(self):
        """Test filename length validation"""
        long_filename = "a" * 300
        assert InputSanitizer.validate_filename(long_filename) == False

    def test_validate_filename_path_traversal(self):
        """Test filename path traversal validation"""
        bad_filename = "../../etc/passwd"
        assert InputSanitizer.validate_filename(bad_filename) == False

    def test_validate_email_valid(self):
        """Test valid email validation"""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "test+tag@gmail.com"
        ]
        for email in valid_emails:
            assert InputSanitizer.validate_email(email) == True

    def test_validate_email_invalid(self):
        """Test invalid email validation"""
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "test@",
            "test..test@example.com",
            "a" * 300 + "@example.com"
        ]
        for email in invalid_emails:
            assert InputSanitizer.validate_email(email) == False


class TestSecurityUtilities:
    """Test security utility functions"""

    def test_generate_secure_token(self):
        """Test secure token generation"""
        token1 = generate_secure_token()
        token2 = generate_secure_token()

        assert len(token1) > 0
        assert token1 != token2  # Should be unique

    def test_constant_time_compare_equal(self):
        """Test constant time comparison for equal strings"""
        assert constant_time_compare("password", "password") == True

    def test_constant_time_compare_different(self):
        """Test constant time comparison for different strings"""
        assert constant_time_compare("password", "wrong") == False

    def test_constant_time_compare_different_lengths(self):
        """Test constant time comparison for different length strings"""
        assert constant_time_compare("short", "longer_string") == False


class TestSecurityMiddleware:
    """Test security middleware integration"""

    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)

    def test_rate_limit_headers(self):
        """Test rate limit headers are added"""
        response = self.client.get("/api/health")

        assert "X-RateLimit-Remaining-Hourly" in response.headers
        assert "X-RateLimit-Remaining-Minutely" in response.headers
        assert "X-RateLimit-Limit-Hourly" in response.headers
        assert "X-RateLimit-Limit-Minutely" in response.headers

    def test_security_headers(self):
        """Test security headers are added"""
        response = self.client.get("/api/health")

        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"
        assert "Strict-Transport-Security" in response.headers

    @patch('app.security.api_rate_limiter')
    def test_rate_limit_exceeded(self, mock_limiter):
        """Test rate limit exceeded response"""
        # Mock rate limiter to always return False
        mock_limiter.is_allowed.return_value = False

        response = self.client.post("/api/moderate", json={"content": "test"})

        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]

    def test_input_validation_invalid_content_type(self):
        """Test input validation for invalid content type"""
        response = self.client.post("/api/moderate", json={
            "content": "test content",
            "content_type": "invalid_type"
        })

        assert response.status_code == 400
        assert "Invalid content type" in response.json()["detail"]

    def test_input_validation_invalid_email(self):
        """Test input validation for invalid email"""
        # This would apply to endpoints that accept email input
        # For now, test the utility function directly
        assert InputSanitizer.validate_email("invalid-email") == False
        assert InputSanitizer.validate_email("valid@example.com") == True

    def test_large_content_handling(self):
        """Test handling of very large content"""
        large_content = "word " * 10000  # Very large content

        response = self.client.post("/api/moderate", json={
            "content": large_content,
            "content_type": "text"
        })

        # Should handle gracefully without crashing
        assert response.status_code in [200, 400]  # Either success or validation error

    def test_malformed_json_handling(self):
        """Test handling of malformed JSON"""
        response = self.client.post(
            "/api/moderate",
            content='{"content": "test", "content_type": "text"',  # Missing closing brace
            headers={"Content-Type": "application/json"}
        )

        # Should handle gracefully
        assert response.status_code != 500  # Not an internal server error

    def test_sql_injection_prevention(self):
        """Test SQL injection prevention through input sanitization"""
        malicious_content = "'; DROP TABLE users; --"

        response = self.client.post("/api/moderate", json={
            "content": malicious_content,
            "content_type": "text"
        })

        # Should sanitize input and not crash
        assert response.status_code in [200, 400]

    def test_xss_prevention(self):
        """Test XSS prevention through input sanitization"""
        xss_content = '<script>alert("xss")</script>'

        response = self.client.post("/api/moderate", json={
            "content": xss_content,
            "content_type": "text"
        })

        # Should sanitize input
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            # If successful, check that script tags are handled
            result = response.json()
            assert "<script>" not in str(result)  # Should be sanitized
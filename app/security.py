#!/usr/bin/env python3
"""
Security middleware for RL-Powered Content Moderation API
Includes rate limiting, input sanitization, and security headers
"""

import os
import secrets
import time
import re
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
import hashlib

logger = logging.getLogger(__name__)

# Security Configuration
class SecurityConfig:
    # Rate Limiting Configuration with safe parsing
    try:
        MAX_REQUESTS_PER_HOUR = int(os.getenv("MAX_REQUESTS_PER_HOUR", "1000"))
    except (ValueError, TypeError):
        MAX_REQUESTS_PER_HOUR = 1000

    try:
        MAX_REQUESTS_PER_MINUTE = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "100"))
    except (ValueError, TypeError):
        MAX_REQUESTS_PER_MINUTE = 100

    try:
        AUTH_MAX_ATTEMPTS = int(os.getenv("AUTH_MAX_ATTEMPTS", "5"))
    except (ValueError, TypeError):
        AUTH_MAX_ATTEMPTS = 5

    try:
        AUTH_LOCKOUT_DURATION = int(os.getenv("AUTH_LOCKOUT_DURATION", "900"))
    except (ValueError, TypeError):
        AUTH_LOCKOUT_DURATION = 900  # 15 minutes

    # Security Headers
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "X-API-Version": "2.0"
    }

config = SecurityConfig()

# Rate Limiting Classes
class RateLimiter:
    """In-memory rate limiter with cleanup"""

    def __init__(self):
        self.requests: Dict[str, list] = {}
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()

    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """Check if request is allowed within rate limit"""
        now = time.time()
        self._cleanup_old_entries()

        if key not in self.requests:
            self.requests[key] = []

        # Remove old entries outside window
        self.requests[key] = [
            timestamp for timestamp in self.requests[key]
            if now - timestamp < window_seconds
        ]

        # Check if under limit
        if len(self.requests[key]) >= max_requests:
            return False

        # Add current request
        self.requests[key].append(now)
        return True

    def _cleanup_old_entries(self):
        """Remove old rate limiting entries with memory-efficient cleanup"""
        now = time.time()
        if now - self.last_cleanup > self.cleanup_interval:
            keys_to_remove = []

            for key in list(self.requests.keys()):
                # Keep only entries within the maximum window (1 hour)
                original_count = len(self.requests[key])
                self.requests[key] = [
                    timestamp for timestamp in self.requests[key]
                    if now - timestamp < 3600
                ]

                # Remove empty entries
                if not self.requests[key]:
                    keys_to_remove.append(key)
                # Log significant cleanup for monitoring
                elif len(self.requests[key]) < original_count * 0.5:  # More than 50% cleaned
                    logger.debug(f"Cleaned up {original_count - len(self.requests[key])} old entries for key {key}")

            # Remove empty keys
            for key in keys_to_remove:
                del self.requests[key]

            # Periodic deep cleanup: remove very old keys entirely
            if len(self.requests) > 10000:  # If we have too many keys
                cutoff_time = now - 7200  # 2 hours ago
                old_keys = []
                for key, timestamps in self.requests.items():
                    if timestamps and max(timestamps) < cutoff_time:
                        old_keys.append(key)

                for key in old_keys[:1000]:  # Clean up to 1000 keys at a time
                    del self.requests[key]

                if old_keys:
                    logger.info(f"Deep cleanup removed {len(old_keys[:1000])} stale rate limit keys")

            self.last_cleanup = now

class AuthRateLimiter:
    """Rate limiter specifically for authentication attempts"""

    def __init__(self):
        self.attempts: Dict[str, Dict[str, Any]] = {}

    def is_locked(self, client_ip: str) -> bool:
        """Check if IP is currently locked out"""
        if client_ip in self.attempts:
            attempt_data = self.attempts[client_ip]
            locked_until = attempt_data.get("locked_until")
            if locked_until and time.time() < locked_until:
                return True
        return False

    def record_attempt(self, client_ip: str, success: bool) -> Dict[str, Any]:
        """Record authentication attempt"""
        current_time = time.time()

        if client_ip not in self.attempts:
            self.attempts[client_ip] = {
                "count": 0,
                "last_attempt": current_time
            }

        attempt_data = self.attempts[client_ip]

        if success:
            # Reset on successful login
            self.attempts[client_ip] = {
                "count": 0,
                "last_attempt": current_time
            }
            return {"locked": False, "attempts_remaining": config.AUTH_MAX_ATTEMPTS}
        else:
            # Increment failed attempts
            attempt_data["count"] += 1
            attempt_data["last_attempt"] = current_time

            if attempt_data["count"] >= config.AUTH_MAX_ATTEMPTS:
                # Lock the IP
                attempt_data["locked_until"] = current_time + config.AUTH_LOCKOUT_DURATION
                return {
                    "locked": True,
                    "locked_until": attempt_data["locked_until"],
                    "attempts_remaining": 0
                }

            return {
                "locked": False,
                "attempts_remaining": config.AUTH_MAX_ATTEMPTS - attempt_data["count"]
            }

# Global rate limiter instances
api_rate_limiter = RateLimiter()
auth_rate_limiter = AuthRateLimiter()

# Input Sanitization
class InputSanitizer:
    """Input sanitization utilities"""

    @staticmethod
    def sanitize_string(input_str: str, max_length: int = 10000) -> str:
        """Sanitize string input"""
        if not isinstance(input_str, str):
            raise ValueError("Input must be a string")

        # Remove null bytes
        cleaned = input_str.replace('\x00', '')

        # Remove dangerous control characters
        cleaned = ''.join(char for char in cleaned
                         if ord(char) >= 32 or char in '\n\t\r')

        # Truncate to max length
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length]

        return cleaned.strip()

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        if not filename:
            raise ValueError("Filename cannot be empty")

        # Remove path traversal attempts
        filename = os.path.basename(filename)

        # Allow only safe characters
        safe_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-")
        filename = ''.join(c for c in filename if c in safe_chars)

        if not filename:
            raise ValueError("Filename contains no valid characters")

        # Ensure reasonable length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:250] + ext

        return filename

    @staticmethod
    def validate_filename(filename: str) -> bool:
        """Validate filename for security"""
        if not filename or len(filename) > 255:
            return False

        # Check for path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return False

        # Check for dangerous characters
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\0']
        return not any(char in filename for char in dangerous_chars)

    @staticmethod
    def validate_content_type(content_type: str) -> bool:
        """Validate content type"""
        allowed_types = ["text", "image", "audio", "video", "code"]
        return content_type in allowed_types

    @staticmethod
    def validate_email(email: str) -> bool:
        """Basic email validation"""
        if not email or not isinstance(email, str):
            return False

        # Basic email pattern check
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email)) and len(email) <= 255

# Security Manager
class SecurityManager:
    """Central security management"""

    def __init__(self):
        self.api_rate_limiter = api_rate_limiter
        self.auth_rate_limiter = auth_rate_limiter

    def get_client_ip(self, request: Request) -> str:
        """Extract client IP with proxy support"""
        # Check for forwarded headers (proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct connection
        if request.client:
            return request.client.host

        return "unknown"

    def check_rate_limit(self, request: Request) -> None:
        """Apply rate limiting to request"""
        client_ip = self.get_client_ip(request)
        path = request.url.path

        # Different limits for different endpoints
        if path.startswith("/api/auth/") or path in ["/api/users/login", "/api/users/register"]:
            # Stricter limits for auth endpoints
            if not self.api_rate_limiter.is_allowed(f"auth:{client_ip}", 10, 3600):  # 10 per hour
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many authentication requests. Please try again later.",
                    headers={"Retry-After": "3600"}
                )
        elif path.startswith("/api/moderate"):
            # Moderate limits for moderation endpoints
            if not self.api_rate_limiter.is_allowed(f"moderate:{client_ip}", config.MAX_REQUESTS_PER_HOUR, 3600):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded for moderation requests.",
                    headers={"Retry-After": "3600"}
                )
        else:
            # General API limits
            if not self.api_rate_limiter.is_allowed(f"api:{client_ip}", config.MAX_REQUESTS_PER_MINUTE, 60):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please try again later.",
                    headers={"Retry-After": "60"}
                )

    def check_auth_rate_limit(self, request: Request) -> None:
        """Check authentication rate limiting"""
        client_ip = self.get_client_ip(request)

        if self.auth_rate_limiter.is_locked(client_ip):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many failed authentication attempts. Please try again later.",
                headers={"Retry-After": str(config.AUTH_LOCKOUT_DURATION)}
            )

    def validate_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize input data"""
        sanitized = {}

        for key, value in data.items():
            if isinstance(value, str):
                # Sanitize strings
                if key in ["content", "text", "comment"]:
                    sanitized[key] = InputSanitizer.sanitize_string(value, 50000)  # Larger limit for content
                elif key in ["filename", "name"]:
                    sanitized[key] = InputSanitizer.sanitize_filename(value)
                elif key == "email":
                    if not InputSanitizer.validate_email(value):
                        raise HTTPException(status_code=400, detail="Invalid email format")
                    sanitized[key] = value.lower().strip()
                elif key == "content_type":
                    if not InputSanitizer.validate_content_type(value):
                        raise HTTPException(status_code=400, detail="Invalid content type")
                    sanitized[key] = value
                else:
                    sanitized[key] = InputSanitizer.sanitize_string(value, 1000)
            elif isinstance(value, (int, float, bool, list, dict)):
                # Allow other types as-is (they should be validated by Pydantic)
                sanitized[key] = value
            else:
                # Convert to string and sanitize
                sanitized[key] = InputSanitizer.sanitize_string(str(value), 1000)

        return sanitized

    def log_security_event(self, event_type: str, details: Dict[str, Any], request: Request):
        """Log security events"""
        client_ip = self.get_client_ip(request)
        user_id = getattr(request.state, 'user_id', None) if hasattr(request, 'state') else None

        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "client_ip": client_ip,
            "user_id": user_id,
            "user_agent": request.headers.get("User-Agent", "unknown"),
            "path": request.url.path,
            "method": request.method,
            "details": details
        }

        logger.warning(f"SECURITY_EVENT: {log_entry}")

# Global security manager instance
security_manager = SecurityManager()

# Security Middleware Functions
def add_security_headers(response, request: Request):
    """Add security headers to response"""
    for header, value in config.SECURITY_HEADERS.items():
        response.headers[header] = value

    # Add rate limit headers
    client_ip = security_manager.get_client_ip(request)
    remaining_hourly = max(0, config.MAX_REQUESTS_PER_HOUR - len(api_rate_limiter.requests.get(f"api:{client_ip}", [])))
    remaining_minutely = max(0, config.MAX_REQUESTS_PER_MINUTE - len(api_rate_limiter.requests.get(f"api:{client_ip}", [])))

    response.headers["X-RateLimit-Remaining-Hourly"] = str(remaining_hourly)
    response.headers["X-RateLimit-Remaining-Minutely"] = str(remaining_minutely)
    response.headers["X-RateLimit-Limit-Hourly"] = str(config.MAX_REQUESTS_PER_HOUR)
    response.headers["X-RateLimit-Limit-Minutely"] = str(config.MAX_REQUESTS_PER_MINUTE)

    return response

async def security_middleware(request: Request, call_next):
    """FastAPI middleware for security checks"""
    try:
        # Apply rate limiting
        security_manager.check_rate_limit(request)

        # Check auth rate limiting for auth endpoints
        if request.url.path.startswith("/api/auth/") or request.url.path in ["/api/users/login", "/api/users/register"]:
            security_manager.check_auth_rate_limit(request)

        # Validate and sanitize input for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.json()
                sanitized_body = security_manager.validate_input(body)
                # Note: In FastAPI, we can't directly modify the request body
                # Validation is performed but original body is preserved
                # Individual endpoints should use validated data from dependencies
            except Exception:
                # If body parsing fails, continue without sanitization
                # This prevents breaking requests with invalid JSON
                pass

        # Process request
        response = await call_next(request)

        # Add security headers
        response = add_security_headers(response, request)

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Security middleware error: {e}")
        # Return generic error response
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )

# Utility Functions
def generate_secure_token(length: int = 32) -> str:
    """Generate cryptographically secure token"""
    return secrets.token_urlsafe(length)

def hash_string(input_str: str) -> str:
    """Create SHA-256 hash of string (for non-sensitive data)"""
    return hashlib.sha256(input_str.encode()).hexdigest()

def constant_time_compare(a: str, b: str) -> bool:
    """Constant time string comparison to prevent timing attacks"""
    if len(a) != len(b):
        return False
    return sum(a[i] != b[i] for i in range(len(a))) == 0

# Security event logging
def log_security_event(event_type: str, details: Dict[str, Any], request: Request):
    """Log security events"""
    security_manager.log_security_event(event_type, details, request)
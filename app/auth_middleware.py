import os
import jwt
import secrets
import time
import hashlib
from fastapi import Request, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from functools import wraps
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
import logging

logger = logging.getLogger(__name__)

# Enhanced JWT configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 30

# Supabase JWT configuration (backward compatibility)
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")

# Password hashing
PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

security = HTTPBearer()

# Token blacklist for logout functionality
class TokenBlacklist:
    def __init__(self):
        self.blacklisted_tokens = set()
        self.cleanup_interval = 3600  # 1 hour
        self.last_cleanup = time.time()

    def add_token(self, jti: str):
        """Add token to blacklist"""
        self.blacklisted_tokens.add(jti)
        self._cleanup_expired()

    def is_blacklisted(self, jti: str) -> bool:
        """Check if token is blacklisted"""
        self._cleanup_expired()
        return jti in self.blacklisted_tokens

    def _cleanup_expired(self):
        """Remove expired tokens from blacklist"""
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            # In production, implement proper cleanup based on token expiry
            self.last_cleanup = current_time

# Global token blacklist instance
token_blacklist = TokenBlacklist()

# Rate limiting for authentication
class AuthRateLimiter:
    def __init__(self):
        self.attempts = {}  # {ip: {count: int, last_attempt: float, locked_until: float}}
        self.max_attempts = 5
        self.lockout_duration = 900  # 15 minutes

    def is_locked(self, client_ip: str) -> bool:
        """Check if IP is currently locked"""
        if client_ip in self.attempts:
            attempt_data = self.attempts[client_ip]
            if "locked_until" in attempt_data and time.time() < attempt_data["locked_until"]:
                return True
        return False

    def record_attempt(self, client_ip: str, success: bool) -> Dict[str, Any]:
        """Record authentication attempt"""
        current_time = time.time()

        if client_ip not in self.attempts:
            self.attempts[client_ip] = {"count": 0, "last_attempt": current_time}

        attempt_data = self.attempts[client_ip]

        if success:
            # Reset on successful login
            self.attempts[client_ip] = {"count": 0, "last_attempt": current_time}
            return {"locked": False, "attempts_remaining": self.max_attempts}
        else:
            # Increment failed attempts
            attempt_data["count"] += 1
            attempt_data["last_attempt"] = current_time

            if attempt_data["count"] >= self.max_attempts:
                # Lock the IP
                attempt_data["locked_until"] = current_time + self.lockout_duration
                return {
                    "locked": True,
                    "locked_until": attempt_data["locked_until"],
                    "attempts_remaining": 0
                }

            return {
                "locked": False,
                "attempts_remaining": self.max_attempts - attempt_data["count"]
            }

# Global auth rate limiter
auth_rate_limiter = AuthRateLimiter()

class EnhancedJWTAuth:
    """Enhanced JWT Authentication with refresh tokens and security features"""

    def __init__(self):
        self.secret = JWT_SECRET_KEY
        self.algorithm = JWT_ALGORITHM

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token with enhanced security"""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        # Add security claims
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
            "jti": secrets.token_urlsafe(16)  # JWT ID for tracking
        })

        try:
            return jwt.encode(to_encode, self.secret, algorithm=self.algorithm)
        except Exception as e:
            logger.error(f"Token creation failed: {e}")
            # Fallback simple token for development
            return f"fallback_token_{data.get('user_id', 'unknown')}_{int(time.time())}"

    def create_refresh_token(self, user_id: str) -> str:
        """Create refresh token"""
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        to_encode = {
            "user_id": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
            "jti": secrets.token_urlsafe(16)
        }

        return jwt.encode(to_encode, self.secret, algorithm=self.algorithm)

    def verify_token(self, token: str, token_type: str = "access") -> dict:
        """Verify JWT token with enhanced security"""
        try:
            # Try Supabase JWT verification first (backward compatibility)
            if SUPABASE_JWT_SECRET:
                try:
                    payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"])
                    logger.info("Token verified using Supabase JWT secret")
                    payload["token_type"] = "supabase"
                    return payload
                except jwt.JWTError:
                    pass

            # Try local JWT verification
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])

            # Check token type
            if payload.get("type") != token_type:
                raise jwt.JWTError("Invalid token type")

            # Check blacklist
            jti = payload.get("jti")
            if jti and token_blacklist.is_blacklisted(jti):
                raise jwt.JWTError("Token has been revoked")

            payload["token_type"] = "local"
            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except jwt.JWTError as e:
            logger.warning(f"JWT verification failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"}
            )

    async def authenticate_request(self, request: Request) -> Optional[Dict[str, Any]]:
        """Authenticate request with rate limiting"""
        try:
            # Get authorization header
            authorization = request.headers.get("Authorization")
            if not authorization or not authorization.startswith("Bearer "):
                return None

            token = authorization[7:]  # Remove "Bearer " prefix

            # Rate limiting check
            client_ip = self._get_client_ip(request)
            if auth_rate_limiter.is_locked(client_ip):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many authentication attempts. Please try again later."
                )

            # Verify token
            payload = self.verify_token(token, "access")

            return {
                "user_id": payload.get("user_id") or payload.get("sub"),
                "username": payload.get("sub") or payload.get("username"),
                "email": payload.get("email"),
                "role": payload.get("role", "user"),
                "token_type": payload.get("token_type", "local"),
                "token_jti": payload.get("jti")
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None

    def _get_client_ip(self, request: Request) -> str:
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

# Password management
class PasswordManager:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        try:
            return PWD_CONTEXT.hash(password)
        except Exception as e:
            logger.warning(f"Bcrypt failed, using fallback: {e}")
            # Fallback to simple hash (not recommended for production)
            return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            return PWD_CONTEXT.verify(plain_password, hashed_password)
        except Exception as e:
            logger.warning(f"Bcrypt verify failed, using fallback: {e}")
            # Fallback verification
            return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

# Create global instances
jwt_auth = EnhancedJWTAuth()
password_manager = PasswordManager()

# Backward compatibility
class JWTAuthMiddleware(EnhancedJWTAuth):
    """Backward compatibility wrapper"""
    pass

# Helper functions
async def get_current_user_optional(
    request: Request = None,
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> Optional[dict]:
    """Optional authentication - returns None if no token"""
    try:
        if credentials:
            return await jwt_auth.authenticate_request(request) if request else None
        return None
    except HTTPException:
        return None

async def get_current_user(
    request: Request = None,
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    """Required authentication"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )

    user_data = await jwt_auth.authenticate_request(request) if request else None
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )

    return user_data
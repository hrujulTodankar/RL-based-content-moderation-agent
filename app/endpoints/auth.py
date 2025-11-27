from fastapi import APIRouter, HTTPException, Depends, status, Request, Form
from fastapi.security import HTTPBearer
from typing import Optional
from datetime import datetime
import uuid
import time
import logging

from app.auth_middleware import (
    jwt_auth, password_manager, auth_rate_limiter, token_blacklist,
    get_current_user
)
from app.schemas import UserRegister, UserLogin, Token, RefreshToken, UserProfile, StandardResponse

logger = logging.getLogger(__name__)

# Simple in-memory user storage (replace with proper database in production)
_users_db = {}

router = APIRouter(prefix="/auth", tags=["Authentication"])

security = HTTPBearer()

class AuthUser:
    """User object for authenticated requests"""
    def __init__(self, user_id: str, username: str, token_jti: str = None,
                 email: str = None, role: str = "user", **kwargs):
        self.user_id = user_id
        self.username = username
        self.token_jti = token_jti
        self.email = email
        self.role = role

async def get_current_user_required(request: Request) -> AuthUser:
    """Get current user (required authentication)"""
    user_data = await get_current_user(request)
    return AuthUser(**user_data)

async def get_current_user_optional(request: Request) -> Optional[AuthUser]:
    """Get current user (optional authentication)"""
    try:
        user_data = await get_current_user(request)
        return AuthUser(**user_data) if user_data else None
    except HTTPException:
        return None

@router.post("/register", response_model=StandardResponse, status_code=201)
async def register_user(user_data: UserRegister, request: Request):
    """Register new user account with enhanced security and standardized response"""
    try:
        # Simple validation
        username = user_data.username.strip()
        if len(username) < 3:
            raise HTTPException(status_code=400, detail="Username must be at least 3 characters")

        # Check if user exists
        if username in _users_db:
            raise HTTPException(status_code=409, detail="Username already exists")

        # Create user
        user_id = str(uuid.uuid4())[:12]

        # Hash password
        password_hash = password_manager.hash_password(user_data.password)

        # Store user
        _users_db[username] = {
            "user_id": user_id,
            "username": username,
            "password_hash": password_hash,
            "email": user_data.email,
            "email_verified": False,
            "role": "user",
            "created_at": time.time(),
            "last_login": None
        }

        # Create tokens
        token_data = {"sub": username, "user_id": user_id}
        access_token = jwt_auth.create_access_token(token_data)
        refresh_token = jwt_auth.create_refresh_token(user_id)

        logger.info(f"User registered: {username}")

        return StandardResponse(
            success=True,
            message="User registered successfully",
            data={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": 1440,
                "user_id": user_id,
                "username": username
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return StandardResponse(
            success=False,
            message=f"Registration failed: {str(e)}",
            error_code="REGISTRATION_ERROR"
        )

@router.post("/login", response_model=Token, status_code=200)
async def login_user(
    request: Request,
    username: Optional[str] = Form(None, description="Username for form-based login"),
    password: Optional[str] = Form(None, description="Password for form-based login")
):
    """
    Login user with standardized format support
    
    This endpoint supports both:
    1. Form data: username and password as form fields (Content-Type: application/x-www-form-urlencoded)
    2. JSON data: username and password in JSON body (Content-Type: application/json)
    
    For external integrations, use JSON format for better compatibility.
    """
    client_ip = request.client.host if request.client else "unknown"

    # Check rate limiting
    if auth_rate_limiter.is_locked(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )

    try:
        # Determine request format and extract credentials
        content_type = request.headers.get("content-type", "").lower()
        
        if "application/json" in content_type:
            # JSON format
            try:
                json_data = await request.json()
                username = json_data.get("username", "").strip()
                password = json_data.get("password", "")
            except Exception as e:
                raise HTTPException(
                    status_code=400, 
                    detail="Invalid JSON format. Expected: {\"username\": \"string\", \"password\": \"string\"}"
                )
        elif "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
            # Form format (already extracted via Form parameters)
            if not username or not password:
                raise HTTPException(
                    status_code=400,
                    detail="Both username and password are required for form-based login"
                )
            username = username.strip()
        else:
            # Default to expecting form data
            if not username or not password:
                raise HTTPException(
                    status_code=400,
                    detail="Please provide username and password. Support both form data and JSON formats."
                )
            username = username.strip()

        # Validate inputs
        if not username:
            raise HTTPException(status_code=400, detail="Username is required")
        if not password:
            raise HTTPException(status_code=400, detail="Password is required")

        # Find user
        if username not in _users_db:
            auth_rate_limiter.record_attempt(client_ip, False)
            raise HTTPException(status_code=401, detail="Invalid username or password")

        user = _users_db[username]

        # Verify password
        if not password_manager.verify_password(password, user["password_hash"]):
            auth_rate_limiter.record_attempt(client_ip, False)
            raise HTTPException(status_code=401, detail="Invalid username or password")

        # Record successful login
        auth_rate_limiter.record_attempt(client_ip, True)
        user["last_login"] = time.time()

        # Create tokens
        token_data = {"sub": username, "user_id": user["user_id"]}
        access_token = jwt_auth.create_access_token(token_data)
        refresh_token = jwt_auth.create_refresh_token(user["user_id"])

        logger.info(f"User logged in: {username}")

        return StandardResponse(
            success=True,
            message="Login successful",
            data={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": 1440,
                "user_id": user["user_id"],
                "username": username
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.post("/refresh", response_model=Token, status_code=200)
async def refresh_token(refresh_data: RefreshToken, request: Request):
    """Refresh access token using refresh token"""
    client_ip = request.client.host if request.client else "unknown"

    try:
        # Verify refresh token
        payload = jwt_auth.verify_token(refresh_data.refresh_token, "refresh")
        user_id = payload.get("user_id")

        # Find user
        user = None
        for u in _users_db.values():
            if u["user_id"] == user_id:
                user = u
                break

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # Create new tokens
        token_data = {"sub": user["username"], "user_id": user["user_id"]}
        access_token = jwt_auth.create_access_token(token_data)
        new_refresh_token = jwt_auth.create_refresh_token(user["user_id"])

        logger.info(f"Token refreshed for user: {user['username']}")

        return StandardResponse(
            success=True,
            message="Token refreshed successfully",
            data={
                "access_token": access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer",
                "expires_in": 1440,
                "user_id": user["user_id"],
                "username": user["username"]
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )

@router.get("/profile", status_code=200, response_model=UserProfile)
async def get_user_profile(current_user: AuthUser = Depends(get_current_user_required)):
    """Get current user profile"""
    try:
        user = _users_db.get(current_user.username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return UserProfile(
            user_id=user["user_id"],
            username=user["username"],
            email=user.get("email"),
            email_verified=user.get("email_verified", False),
            role=user.get("role", "user"),
            created_at=datetime.fromtimestamp(user["created_at"]).isoformat(),
            last_login=datetime.fromtimestamp(user["last_login"]).isoformat() if user.get("last_login") else None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile retrieval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve profile"
        )

@router.post("/logout", status_code=200)
async def logout_user(request: Request, current_user: AuthUser = Depends(get_current_user_required)):
    """Logout user (invalidate token)"""
    client_ip = request.client.host if request.client else "unknown"

    # Add token to blacklist to invalidate it
    if current_user.token_jti:
        token_blacklist.add_token(current_user.token_jti)
        logger.info(f"Token blacklisted for user: {current_user.username}")

    return {"message": "Logged out successfully", "token_invalidated": True}

@router.get("/debug-users", status_code=200)
async def debug_users():
    """Debug endpoint to list all users (development only)"""
    # This should be removed in production
    return {
        "users": [
            {
                "username": username,
                "user_id": user["user_id"],
                "email": user.get("email"),
                "created_at": datetime.fromtimestamp(user["created_at"]).isoformat()
            }
            for username, user in _users_db.items()
        ],
        "total_users": len(_users_db)
    }
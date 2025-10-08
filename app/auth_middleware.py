import os
import jwt
from fastapi import Request, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# Supabase JWT configuration
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "your-jwt-secret")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
ALGORITHM = "HS256"

security = HTTPBearer()

class JWTAuthMiddleware:
    """JWT Authentication Middleware for Supabase"""
    
    def __init__(self, secret: str = None, algorithm: str = "HS256"):
        self.secret = secret or SUPABASE_JWT_SECRET
        self.algorithm = algorithm
    
    def verify_token(self, token: str) -> dict:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],
                options={"verify_signature": True}
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.error("Token has expired")
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {str(e)}")
            raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    async def __call__(
        self, 
        credentials: HTTPAuthorizationCredentials = Security(security)
    ) -> dict:
        """Middleware callable for FastAPI dependency injection"""
        if not credentials:
            raise HTTPException(
                status_code=401,
                detail="Authorization header missing"
            )
        
        token = credentials.credentials
        payload = self.verify_token(token)
        
        # Extract user info
        user_id = payload.get("sub")
        user_role = payload.get("role", "user")
        
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token payload"
            )
        
        return {
            "user_id": user_id,
            "role": user_role,
            "email": payload.get("email"),
            "payload": payload
        }

# Create global instance
jwt_auth = JWTAuthMiddleware()

# Helper function for optional authentication
async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    """Optional authentication - returns None if no token"""
    try:
        if credentials:
            return await jwt_auth(credentials)
    except HTTPException:
        pass
    return None
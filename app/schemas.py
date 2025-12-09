from pydantic import BaseModel, Field, validator
from typing import Optional, Any, Dict, List, Union
from datetime import datetime
import uuid

# Standard API response format
class StandardResponse(BaseModel):
    """Standardized API response format for consistency"""
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Human-readable response message")
    data: Optional[Any] = Field(None, description="Response data payload")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Response timestamp")
    error_code: Optional[str] = Field(None, description="Error code if applicable")
    meta: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    request_id: Optional[str] = Field(None, description="Unique request identifier")

# Error response schema
class ErrorResponse(BaseModel):
    """Standardized error response format"""
    success: bool = Field(False, description="Always false for errors")
    message: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Specific error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Unique request identifier")

# Pagination schema
class PaginationMeta(BaseModel):
    """Standardized pagination metadata"""
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Items per page")
    total_items: int = Field(..., ge=0, description="Total number of items")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_prev: bool = Field(..., description="Whether there are previous pages")

class PaginatedResponse(BaseModel):
    """Standardized paginated response format"""
    success: bool = Field(True, description="Always true for paginated responses")
    message: str = Field("Data retrieved successfully", description="Response message")
    data: List[Any] = Field(..., description="Data items")
    meta: PaginationMeta = Field(..., description="Pagination metadata")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Response timestamp")
    request_id: Optional[str] = Field(None, description="Unique request identifier")

# Authentication schemas
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    email: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

class UserLogin(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    username: str

class RefreshToken(BaseModel):
    refresh_token: str

class UserProfile(BaseModel):
    user_id: str
    username: str
    email: Optional[str]
    email_verified: bool
    role: str
    created_at: str
    last_login: Optional[str]

# Existing schemas
class FeedbackPayload(BaseModel):
    content_id: str
    user_id: str
    feedback_type: str = Field(..., pattern="^(positive|negative)$")
    comment: Optional[str] = None

class ModerationRequest(BaseModel):
    content_id: str
    content_data: str  # Can be text, a URL, or base64 encoded data
    content_type: str = Field(..., pattern="^(text|image|video)$")

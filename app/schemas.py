from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

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

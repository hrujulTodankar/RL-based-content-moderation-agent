from pydantic import BaseModel, Field
from typing import Optional

class FeedbackPayload(BaseModel):
    content_id: str
    user_id: str
    feedback_type: str = Field(..., pattern="^(positive|negative)$")
    comment: Optional[str] = None

class ModerationRequest(BaseModel):
    content_id: str
    content_data: str  # Can be text, a URL, or base64 encoded data
    content_type: str = Field(..., pattern="^(text|image|video)$")

from fastapi import APIRouter, HTTPException, File, UploadFile, Form, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
from datetime import datetime
import uuid

from ..moderation_agent import ModerationAgent
from ..feedback_handler import FeedbackHandler
from ..event_queue import EventQueue

logger = logging.getLogger(__name__)

# Initialize components
moderation_agent = ModerationAgent()
feedback_handler = FeedbackHandler()
event_queue = EventQueue()

router = APIRouter()

class ModerationResponse(BaseModel):
    moderation_id: str
    flagged: bool
    score: float
    confidence: float
    content_type: str
    reasons: list[str]
    timestamp: str

@router.post("/moderate/file")
async def moderate_file(
    file: UploadFile = File(...),
    content_type: str = Form(...),
    mcp_metadata: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = None
):
    """
    Moderate uploaded files (images, audio, video)
    Handles large files asynchronously with proper error handling
    """
    # For demo purposes, skip authentication
    """
    Moderate uploaded files (images, audio, video)
    Handles large files asynchronously with proper error handling
    """
    try:
        moderation_id = str(uuid.uuid4())

        # Validate file size (10MB limit for images)
        MAX_SIZE = 10 * 1024 * 1024
        content = await file.read()
        if len(content) > MAX_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: {MAX_SIZE} bytes (10MB)"
            )

        # Validate content type
        valid_types = ["image", "audio", "video"]
        if content_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid content_type for file. Must be one of: {valid_types}"
            )

        # Parse MCP metadata if provided
        mcp_meta = None
        if mcp_metadata:
            import json
            mcp_meta = json.loads(mcp_metadata)

        # Process file content
        file_metadata = {
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(content)
        }

        # Run moderation
        result = await moderation_agent.moderate(
            content=content,
            content_type=content_type,
            metadata={"file": file_metadata, "mcp_metadata": mcp_meta}
        )

        moderation_record = {
            "moderation_id": moderation_id,
            "content_type": content_type,
            "flagged": result["flagged"],
            "score": result["score"],
            "confidence": result["confidence"],
            "reasons": result["reasons"],
            "timestamp": datetime.utcnow().isoformat()
        }

        await feedback_handler.store_moderation(moderation_record)

        background_tasks.add_task(
            event_queue.emit,
            "file_moderation_completed",
            moderation_record
        )

        return ModerationResponse(**moderation_record)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File moderation error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="File processing error")
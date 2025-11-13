from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import asyncio
import logging
from datetime import datetime
import json
import uuid

from ..auth_middleware import jwt_auth, get_current_user_optional
from ..observability import track_performance, structured_logger, set_user_context

# For demo purposes, disable authentication
async def demo_user():
    return {"user_id": "demo-user"}
from ..integration_services import integration_services
from ..moderation_agent import ModerationAgent
from ..feedback_handler import FeedbackHandler
from ..event_queue import EventQueue
from ..logger_middleware import LoggerMiddleware

logger = logging.getLogger(__name__)

# Initialize components
moderation_agent = ModerationAgent()
feedback_handler = FeedbackHandler()
event_queue = EventQueue()

router = APIRouter()

# Pydantic models
class ModerationRequest(BaseModel):
    content: str
    content_type: str = Field(..., description="text, image, audio, video, code")
    metadata: Optional[Dict[str, Any]] = None
    mcp_metadata: Optional[Dict[str, Any]] = None

class ModerationResponse(BaseModel):
    moderation_id: str
    flagged: bool
    score: float
    confidence: float
    content_type: str
    reasons: List[str]
    mcp_weighted_score: Optional[float] = None
    timestamp: str

@router.post("/moderate", response_model=ModerationResponse)
@track_performance("content_moderation")
async def moderate_content(
    request: ModerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Moderate content with RL-powered decision making
    Now integrated with NLP context and observability
    """
    # For demo purposes, use default user
    user_id = "demo-user"
    start_time = datetime.utcnow()

    try:
        moderation_id = str(uuid.uuid4())
        logger.info(f"Moderation request {moderation_id} for {request.content_type}")

        # Set user context for observability
        set_user_context(user_id, "demo-user")

        # Get NLP context if text or code
        nlp_context = None
        if request.content_type in ["text", "code"]:
            nlp_result = await integration_services.get_nlp_context(
                request.content,
                request.content_type
            )
            if nlp_result["success"]:
                nlp_context = nlp_result["data"]
                # Merge NLP context into metadata
                if not request.metadata:
                    request.metadata = {}
                request.metadata["nlp_context"] = nlp_context

        # Validate content type
        valid_types = ["text", "image", "audio", "video", "code"]
        if request.content_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid content_type. Must be one of: {valid_types}"
            )

        # Process through MCP if metadata available
        if request.mcp_metadata:
            from ..mcp_integration import MCPIntegrator
            mcp_integrator = MCPIntegrator()
            mcp_result = await mcp_integrator.process(
                content=request.content,
                content_type=request.content_type,
                mcp_metadata=request.mcp_metadata
            )
            enhanced_metadata = {
                **(request.metadata or {}),
                "mcp": mcp_result
            }
        else:
            enhanced_metadata = request.metadata or {}

        # Run moderation agent
        result = await moderation_agent.moderate(
            content=request.content,
            content_type=request.content_type,
            metadata=enhanced_metadata
        )

        # Store moderation result
        moderation_record = {
            "moderation_id": moderation_id,
            "content_type": request.content_type,
            "flagged": result["flagged"],
            "score": result["score"],
            "confidence": result["confidence"],
            "mcp_weighted_score": result.get("mcp_weighted_score"),
            "reasons": result["reasons"],
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "state": result.get("state")  # Store state for RL learning
        }

        # Store moderation result (skip if database not initialized)
        try:
            await feedback_handler.store_moderation(moderation_record)
        except Exception as e:
            logger.warning(f"Failed to store moderation result: {str(e)}")

        # Emit event to queue for analytics
        background_tasks.add_task(
            event_queue.emit,
            "moderation_completed",
            moderation_record
        )

        # Log structured moderation event
        duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        structured_logger.log_moderation_event(
            content_type=request.content_type,
            flagged=result["flagged"],
            score=result["score"],
            user_id=user_id,
            duration_ms=duration_ms
        )

        return ModerationResponse(**moderation_record)

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Moderation error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal moderation error")
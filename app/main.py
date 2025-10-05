from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import asyncio
import logging
from datetime import datetime
import json
import uuid
import os
from pathlib import Path

from moderation_agent import ModerationAgent
from feedback_handler import FeedbackHandler
from mcp_integration import MCPIntegrator
from event_queue import EventQueue
from logger_middleware import LoggerMiddleware

# Create logs directory if it doesn't exist
log_dir = Path(__file__).parent.parent / 'logs'
log_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="RL-Powered Content Moderation API", version="2.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom logging middleware
app.add_middleware(LoggerMiddleware)

# Initialize components
moderation_agent = ModerationAgent()
feedback_handler = FeedbackHandler()
mcp_integrator = MCPIntegrator()
event_queue = EventQueue()

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

class FeedbackRequest(BaseModel):
    moderation_id: str
    feedback_type: str = Field(..., description="thumbs_up, thumbs_down")
    user_id: Optional[str] = None
    comment: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)

class FeedbackResponse(BaseModel):
    feedback_id: str
    moderation_id: str
    status: str
    reward_value: float
    timestamp: str

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting RL-Powered Content Moderation API")
    await event_queue.initialize()
    await feedback_handler.initialize()
    logger.info("All services initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down services")
    await event_queue.close()
    await feedback_handler.close()

@app.get("/")
async def root():
    return {
        "message": "RL-Powered Content Moderation API",
        "version": "2.0",
        "status": "running"
    }

@app.post("/moderate", response_model=ModerationResponse)
async def moderate_content(
    request: ModerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Moderate content with MCP-aware RL agent
    Handles all content types: text, image, audio, video, code
    """
    try:
        moderation_id = str(uuid.uuid4())
        logger.info(f"Moderation request {moderation_id} for {request.content_type}")
        
        # Validate content type
        valid_types = ["text", "image", "audio", "video", "code"]
        if request.content_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid content_type. Must be one of: {valid_types}"
            )
        
        # Process through MCP if metadata available
        if request.mcp_metadata:
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
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await feedback_handler.store_moderation(moderation_record)
        
        # Emit event to queue for analytics
        background_tasks.add_task(
            event_queue.emit,
            "moderation_completed",
            moderation_record
        )
        
        return ModerationResponse(**moderation_record)
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Moderation error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal moderation error")

@app.post("/moderate/file")
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
    try:
        moderation_id = str(uuid.uuid4())
        
        # Validate file size (100MB limit)
        MAX_SIZE = 100 * 1024 * 1024
        content = await file.read()
        if len(content) > MAX_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: {MAX_SIZE} bytes"
            )
        
        # Validate content type
        valid_types = ["image", "audio", "video"]
        if content_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid content_type for file. Must be one of: {valid_types}"
            )
        
        # Parse MCP metadata if provided
        mcp_meta = json.loads(mcp_metadata) if mcp_metadata else None
        
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

@app.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    feedback: FeedbackRequest,
    background_tasks: BackgroundTasks
):
    """
    Accept user feedback (thumbs up/down) and update RL agent
    Integrates with Omkar RL, Ashmit analytics, and Aditya NLP
    """
    try:
        feedback_id = str(uuid.uuid4())
        logger.info(f"Feedback {feedback_id} for moderation {feedback.moderation_id}")
        
        # Validate feedback type
        if feedback.feedback_type not in ["thumbs_up", "thumbs_down"]:
            raise HTTPException(
                status_code=400,
                detail="feedback_type must be 'thumbs_up' or 'thumbs_down'"
            )
        
        # Normalize feedback to reward value
        reward_value = feedback_handler.normalize_feedback(
            feedback_type=feedback.feedback_type,
            rating=feedback.rating
        )
        
        # Store feedback
        feedback_record = {
            "feedback_id": feedback_id,
            "moderation_id": feedback.moderation_id,
            "user_id": feedback.user_id,
            "feedback_type": feedback.feedback_type,
            "rating": feedback.rating,
            "comment": feedback.comment,
            "reward_value": reward_value,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await feedback_handler.store_feedback(feedback_record)
        
        # Update RL agent with reward
        await moderation_agent.update_with_feedback(
            moderation_id=feedback.moderation_id,
            reward=reward_value
        )
        
        # Emit events to integrated services
        background_tasks.add_task(
            emit_feedback_events,
            feedback_record
        )
        
        return FeedbackResponse(
            feedback_id=feedback_id,
            moderation_id=feedback.moderation_id,
            status="processed",
            reward_value=reward_value,
            timestamp=feedback_record["timestamp"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Feedback processing error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Feedback processing error")

async def emit_feedback_events(feedback_record: Dict[str, Any]):
    """Emit feedback events to all integrated services"""
    try:
        # Emit to Omkar RL service
        await event_queue.emit(
            "feedback_omkar_rl",
            {
                "service": "omkar_rl",
                "event_type": "user_feedback",
                **feedback_record
            }
        )
        
        # Emit to Ashmit BHIV analytics
        await event_queue.emit(
            "feedback_bhiv_analytics",
            {
                "service": "ashmit_analytics",
                "event_type": "sentiment_feedback",
                **feedback_record
            }
        )
        
        # Emit to Aditya NLP service
        await event_queue.emit(
            "feedback_nlp_confidence",
            {
                "service": "aditya_nlp",
                "event_type": "confidence_update",
                **feedback_record
            }
        )
        
        logger.info(f"Feedback events emitted for {feedback_record['feedback_id']}")
    except Exception as e:
        logger.error(f"Error emitting feedback events: {str(e)}")

@app.get("/feedback/{moderation_id}")
async def get_feedback(moderation_id: str):
    """Get all feedback for a specific moderation"""
    try:
        feedbacks = await feedback_handler.get_feedback_by_moderation(moderation_id)
        return {"moderation_id": moderation_id, "feedbacks": feedbacks}
    except Exception as e:
        logger.error(f"Error retrieving feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving feedback")

@app.get("/stats")
async def get_stats():
    """Get moderation and feedback statistics"""
    try:
        stats = await feedback_handler.get_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error retrieving stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving statistics")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "moderation_agent": "running",
            "feedback_handler": "running",
            "event_queue": "running",
            "mcp_integrator": "running"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
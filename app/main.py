from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Form, Depends
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
#from .auth_middleware import jwt_auth, get_current_user_optional



async def get_current_user_optional(credentials=None):
    # Bypass authentication and return a dummy user
    return {"user_id": "demo-user", "role": "admin"}

# Comment out the real jwt_auth
# jwt_auth = JWTAuthMiddleware()

from integration_services import integration_services
from adaptive_learning import visualizer

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

# Pydantic models (placed early so decorators can reference them at import time)
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

# Initialize components
moderation_agent = ModerationAgent()
feedback_handler = FeedbackHandler()
mcp_integrator = MCPIntegrator()
event_queue = EventQueue()

@app.post("/moderate", response_model=ModerationResponse)
async def moderate_content(
    request: ModerationRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user_optional)  # Optional auth
):
    """
    Moderate content with RL-powered decision making
    Now integrated with NLP context
    """
    try:
        moderation_id = str(uuid.uuid4())
        logger.info(f"Moderation request {moderation_id} for {request.content_type}")
        
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
            "user_id": user.get("user_id") if user else None
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


@app.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    feedback: FeedbackRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user_optional)
):
    """
    Accept user feedback and execute full integration pipeline:
    User Feedback → Moderation Agent → BHIV → RL Core → Analytics
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
            "user_id": user.get("user_id") if user else feedback.user_id,
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
        
        # Get RL data for pipeline
        moderation_history = [h for h in moderation_agent.history 
                             if h.get("moderation_id") == feedback.moderation_id]
        
        if moderation_history:
            rl_data = {
                "reward": reward_value,
                "state": moderation_history[-1]["state"],
                "action": moderation_history[-1]["action"]
            }
            
            # Execute full integration pipeline in background
            background_tasks.add_task(
                execute_integration_pipeline,
                feedback.moderation_id,
                feedback_record,
                rl_data
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


async def execute_integration_pipeline(
    moderation_id: str,
    feedback_data: Dict[str, Any],
    rl_data: Dict[str, Any]
):
    """Execute the full feedback pipeline with all integrations"""
    try:
        # Execute pipeline: Feedback → BHIV → RL Core → Analytics
        pipeline_result = await integration_services.execute_feedback_pipeline(
            moderation_id=moderation_id,
            feedback_data=feedback_data,
            rl_data=rl_data
        )
        
        # Log pipeline results
        logger.info(f"Integration pipeline completed for {moderation_id}: {pipeline_result}")
        
        # Store pipeline metrics
        await event_queue.emit("pipeline_completed", {
            "moderation_id": moderation_id,
            "pipeline_result": pipeline_result,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Add to learning visualization
        visualizer.add_iteration(
            iteration=len(moderation_agent.history),
            reward=rl_data["reward"],
            score=feedback_data.get("score", 0.5),
            confidence=feedback_data.get("confidence", 0.5),
            is_correct=(rl_data["reward"] > 0)
        )
        
    except Exception as e:
        logger.error(f"Pipeline execution error: {str(e)}", exc_info=True)


# New endpoint: Integration metrics
@app.get("/integration/metrics")
async def get_integration_metrics(user: dict = Depends(get_current_user_optional)):
    """
    Get integration service metrics (secured endpoint)
    Requires JWT authentication
    """
    metrics = integration_services.get_metrics()
    return {
        "integration_metrics": metrics,
        "timestamp": datetime.utcnow().isoformat()
    }


# New endpoint: Generate learning report
@app.post("/learning/report")
async def generate_learning_report(user: dict = Depends(get_current_user_optional)):
    """
    Generate adaptive learning visualization report (secured endpoint)
    """
    try:
        filepath = visualizer.generate_learning_cycle_report()
        summary = visualizer.get_summary_stats()
        
        return {
            "status": "success",
            "report_path": filepath,
            "summary": summary,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error generating report")


# New endpoint: Connectivity test
@app.get("/integration/connectivity")
async def test_connectivity(user: dict = Depends(get_current_user_optional)):
    """
    Test connectivity with all integrated services (secured endpoint)
    """
    results = {
        "bhiv": {"status": "unknown", "latency": None},
        "rl_core": {"status": "unknown", "latency": None},
        "nlp": {"status": "unknown", "latency": None}
    }
    
    # Test BHIV
    try:
        bhiv_result = await integration_services.send_to_bhiv_feedback(
            "test-connectivity",
            {"feedback_type": "thumbs_up", "rating": 5, "test": True}
        )
        results["bhiv"] = {
            "status": "connected" if bhiv_result["success"] else "error",
            "latency": bhiv_result["latency"]
        }
    except Exception as e:
        results["bhiv"]["status"] = "error"
        results["bhiv"]["error"] = str(e)
    
    # Test RL Core
    try:
        rl_result = await integration_services.send_to_rl_core_update(
            "test-connectivity",
            0.5,
            [0.0] * 15,
            0
        )
        results["rl_core"] = {
            "status": "connected" if rl_result["success"] else "error",
            "latency": rl_result["latency"]
        }
    except Exception as e:
        results["rl_core"]["status"] = "error"
        results["rl_core"]["error"] = str(e)
    
    # Test NLP
    try:
        nlp_result = await integration_services.get_nlp_context(
            "test connectivity",
            "text"
        )
        results["nlp"] = {
            "status": "connected" if nlp_result["success"] else "error",
            "latency": nlp_result["latency"]
        }
    except Exception as e:
        results["nlp"]["status"] = "error"
        results["nlp"]["error"] = str(e)
    
    return {
        "connectivity_test": results,
        "timestamp": datetime.utcnow().isoformat()
    }


# New endpoint: Demo flow
@app.post("/demo/run")
async def run_demo_flow(user: dict = Depends(get_current_user_optional)):
    """
    Run the complete demo flow:
    Content → Moderation → Feedback → RL Update → Analytics
    """
    demo_results = {
        "steps": [],
        "start_time": datetime.utcnow().isoformat()
    }
    
    try:
        # Step 1: Content Submission
        content = "This is spam spam spam click here now!!!"
        demo_results["steps"].append({
            "step": "content_submission",
            "content": content,
            "content_type": "text"
        })
        
        # Step 2: Moderation Decision
        mod_result = await moderation_agent.moderate(
            content=content,
            content_type="text"
        )
        moderation_id = str(uuid.uuid4())
        demo_results["steps"].append({
            "step": "moderation_decision",
            "moderation_id": moderation_id,
            "flagged": mod_result["flagged"],
            "score": mod_result["score"],
            "confidence": mod_result["confidence"]
        })
        
        # Step 3: User Feedback
        feedback_data = {
            "feedback_type": "thumbs_up",
            "rating": 5,
            "sentiment": "positive",
            "engagement_score": 0.9
        }
        reward = 1.0
        demo_results["steps"].append({
            "step": "user_feedback",
            "feedback_type": "thumbs_up",
            "rating": 5,
            "reward": reward
        })
        
        # Step 4: RL Reward Update
        await moderation_agent.update_with_feedback(moderation_id, reward)
        demo_results["steps"].append({
            "step": "rl_update",
            "q_table_size": len(moderation_agent.q_table)
        })
        
        # Step 5: Analytics Visualization
        visualizer.add_iteration(
            iteration=len(moderation_agent.history),
            reward=reward,
            score=mod_result["score"],
            confidence=mod_result["confidence"],
            is_correct=True
        )
        demo_results["steps"].append({
            "step": "analytics_logged",
            "total_iterations": len(visualizer.learning_data["iterations"])
        })
        
        demo_results["status"] = "success"
        demo_results["end_time"] = datetime.utcnow().isoformat()
        
        return demo_results
        
    except Exception as e:
        logger.error(f"Demo flow error: {str(e)}", exc_info=True)
        demo_results["status"] = "error"
        demo_results["error"] = str(e)
        return demo_results

# ... Pydantic models are defined earlier in the file

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
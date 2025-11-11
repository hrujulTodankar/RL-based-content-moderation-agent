from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import asyncio
import logging
from datetime import datetime
import json
import uuid

# from ..auth_middleware import jwt_auth, get_current_user_optional
from ..integration_services import integration_services
from ..moderation_agent import ModerationAgent
from ..feedback_handler import FeedbackHandler
from ..event_queue import EventQueue
# from ..adaptive_learning import visualizer

logger = logging.getLogger(__name__)

# Initialize components
moderation_agent = ModerationAgent()
feedback_handler = FeedbackHandler()
event_queue = EventQueue()

router = APIRouter()

# Pydantic models
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
        # visualizer.add_iteration(
        #     iteration=len(moderation_agent.history),
        #     reward=rl_data["reward"],
        #     score=feedback_data.get("score", 0.5),
        #     confidence=feedback_data.get("confidence", 0.5),
        #     is_correct=(rl_data["reward"] > 0)
        # )

    except Exception as e:
        logger.error(f"Pipeline execution error: {str(e)}", exc_info=True)

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

@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    feedback: FeedbackRequest,
    background_tasks: BackgroundTasks,
    user: Optional[Dict[str, Any]] = None
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

        # Get RL data for pipeline
        moderation_history = [h for h in moderation_agent.history
                             if h.get("moderation_id") == feedback.moderation_id]

        if moderation_history:
            rl_data = {
                "reward": reward_value,
                "state": moderation_history[-1]["state"],
                "action": moderation_history[-1]["action"]
            }

            # Send to BHIV InsightFlow for analytics
            background_tasks.add_task(
                integration_services.send_to_bhiv_feedback,
                feedback.moderation_id,
                {
                    "feedback_type": feedback.feedback_type,
                    "rating": feedback.rating,
                    "reward_value": reward_value,
                    "sentiment": "positive" if reward_value > 0 else "negative",
                    "engagement_score": abs(reward_value),
                    "metadata": {
                        "user_id": feedback.user_id,
                        "comment": feedback.comment
                    }
                }
            )

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
        raise HTTPException(status_code=500, detail=f"Feedback processing error: {str(e)}")

@router.get("/feedback/{moderation_id}")
async def get_feedback(moderation_id: str):
    """Get all feedback for a specific moderation"""
    try:
        feedbacks = await feedback_handler.get_feedback_by_moderation(moderation_id)
        return {"moderation_id": moderation_id, "feedbacks": feedbacks}
    except Exception as e:
        logger.error(f"Error retrieving feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving feedback")
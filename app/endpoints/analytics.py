from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict, Any
import logging
from datetime import datetime

from ..auth_middleware import jwt_auth, get_current_user_optional
from ..integration_services import integration_services
from ..feedback_handler import FeedbackHandler
from ..adaptive_learning import visualizer

logger = logging.getLogger(__name__)

# Initialize components
feedback_handler = FeedbackHandler()

router = APIRouter()

@router.get("/stats")
async def get_stats():
    """Get moderation and feedback statistics"""
    try:
        stats = await feedback_handler.get_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error retrieving stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving statistics")

@router.get("/integration/metrics")
async def get_integration_metrics(user: dict = Depends(jwt_auth)):
    """
    Get integration service metrics (secured endpoint)
    Requires JWT authentication
    """
    metrics = integration_services.get_metrics()
    return {
        "integration_metrics": metrics,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/learning/report")
async def generate_learning_report(user: dict = Depends(jwt_auth)):
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

@router.get("/learning/live")
async def get_live_learning_data(user: dict = Depends(jwt_auth)):
    """
    Get live adaptive learning data for real-time visualization (secured endpoint)
    """
    try:
        live_data = visualizer.get_live_data()
        return {
            "live_data": live_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting live data: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error retrieving live data")

@router.get("/integration/connectivity")
async def test_connectivity(user: dict = Depends(jwt_auth)):
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

@router.post("/demo/run")
async def run_demo_flow(user: dict = Depends(jwt_auth)):
    """
    Run the complete demo flow:
    Content → Moderation → Feedback → RL Update → Analytics
    """
    from ..moderation_agent import ModerationAgent
    from ..event_queue import EventQueue

    demo_results = {
        "steps": [],
        "start_time": datetime.utcnow().isoformat()
    }

    try:
        moderation_agent = ModerationAgent()
        event_queue = EventQueue()

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
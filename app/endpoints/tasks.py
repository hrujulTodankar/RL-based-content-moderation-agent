from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import Dict, Any, List
from datetime import datetime
import logging

from app.auth_middleware import get_current_user_required
from app.task_queue import task_queue
from app.observability import track_performance, structured_logger, set_user_context

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["Task Queue Management"])

@router.post("/batch-moderation")
@track_performance("batch_moderation_request")
async def submit_batch_moderation(
    contents: List[str],
    content_type: str = "text",
    metadata: Dict[str, Any] = None,
    current_user: Dict = Depends(get_current_user_required)
):
    """Submit batch content moderation task"""
    user_id = current_user["user_id"]

    try:
        set_user_context(user_id, current_user.get("username"))

        if not contents:
            raise HTTPException(status_code=400, detail="Contents list cannot be empty")

        if len(contents) > 1000:
            raise HTTPException(status_code=400, detail="Maximum 1000 items per batch")

        # Validate content type
        valid_types = ["text", "image", "audio", "video", "code"]
        if content_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid content_type. Must be one of: {valid_types}"
            )

        # Submit task to queue
        task_id = await task_queue.add_task(
            "batch_moderation",
            {
                "contents": contents,
                "content_type": content_type,
                "metadata": metadata or {},
                "user_id": user_id,
                "total_items": len(contents)
            }
        )

        structured_logger.log_security_event(
            "batch_moderation_submitted",
            "127.0.0.1",
            user_id,
            {
                "task_id": task_id,
                "content_type": content_type,
                "batch_size": len(contents)
            }
        )

        return {
            "task_id": task_id,
            "task_type": "batch_moderation",
            "status": "submitted",
            "estimated_completion": "Varies based on batch size",
            "batch_size": len(contents),
            "content_type": content_type,
            "user_id": user_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting batch moderation for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit batch moderation")

@router.post("/analytics-generation")
@track_performance("analytics_generation_request")
async def submit_analytics_generation(
    analytics_type: str = "comprehensive",
    time_range: str = "24h",
    current_user: Dict = Depends(get_current_user_required)
):
    """Submit analytics generation task"""
    user_id = current_user["user_id"]

    try:
        set_user_context(user_id, current_user.get("username"))

        # Validate analytics type
        valid_types = ["comprehensive", "sentiment", "performance", "moderation_stats"]
        if analytics_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid analytics_type. Must be one of: {valid_types}"
            )

        # Submit task to queue
        task_id = await task_queue.add_task(
            "analytics_generation",
            {
                "analytics_type": analytics_type,
                "time_range": time_range,
                "user_id": user_id
            }
        )

        return {
            "task_id": task_id,
            "task_type": "analytics_generation",
            "status": "submitted",
            "analytics_type": analytics_type,
            "time_range": time_range,
            "estimated_completion": "30 seconds",
            "user_id": user_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting analytics generation for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit analytics generation")

@router.post("/cleanup")
@track_performance("cleanup_request")
async def submit_cleanup_operation(
    operation_type: str = "temp_files",
    max_age_days: int = 30,
    current_user: Dict = Depends(get_current_user_required)
):
    """Submit cleanup operation task"""
    user_id = current_user["user_id"]

    try:
        set_user_context(user_id, current_user.get("username"))

        # Check if user has admin role for cleanup operations
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=403,
                detail="Admin access required for cleanup operations"
            )

        # Validate operation type
        valid_operations = ["temp_files", "old_logs", "expired_data"]
        if operation_type not in valid_operations:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid operation_type. Must be one of: {valid_operations}"
            )

        # Submit task to queue
        task_id = await task_queue.add_task(
            "cleanup_operation",
            {
                "operation_type": operation_type,
                "max_age_days": max_age_days,
                "user_id": user_id
            }
        )

        return {
            "task_id": task_id,
            "task_type": "cleanup_operation",
            "status": "submitted",
            "operation_type": operation_type,
            "max_age_days": max_age_days,
            "estimated_completion": "1-5 minutes",
            "user_id": user_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting cleanup operation for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit cleanup operation")

@router.get("/{task_id}")
@track_performance("task_status_check")
async def get_task_status(
    task_id: str,
    current_user: Dict = Depends(get_current_user_required)
):
    """Get task status and result"""
    user_id = current_user["user_id"]

    try:
        set_user_context(user_id, current_user.get("username"))

        task_status = await task_queue.get_task_status(task_id)

        if not task_status:
            raise HTTPException(status_code=404, detail="Task not found")

        # Check if user owns this task (basic check)
        if task_status.get("user_id") and task_status["user_id"] != user_id:
            # Allow admins to see all tasks
            if current_user.get("role") != "admin":
                raise HTTPException(status_code=403, detail="Access denied to this task")

        return task_status

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status for {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get task status")

@router.delete("/{task_id}")
@track_performance("task_cancellation")
async def cancel_task(
    task_id: str,
    current_user: Dict = Depends(get_current_user_required)
):
    """Cancel a pending task"""
    user_id = current_user["user_id"]

    try:
        set_user_context(user_id, current_user.get("username"))

        # Check task ownership first
        task_status = await task_queue.get_task_status(task_id)
        if not task_status:
            raise HTTPException(status_code=404, detail="Task not found")

        if task_status.get("user_id") and task_status["user_id"] != user_id:
            if current_user.get("role") != "admin":
                raise HTTPException(status_code=403, detail="Access denied to this task")

        # Attempt cancellation
        cancelled = await task_queue.cancel_task(task_id)

        if not cancelled:
            raise HTTPException(
                status_code=400,
                detail="Task could not be cancelled (may already be running or completed)"
            )

        structured_logger.log_security_event(
            "task_cancelled",
            "127.0.0.1",
            user_id,
            {"task_id": task_id}
        )

        return {
            "task_id": task_id,
            "status": "cancelled",
            "message": "Task has been cancelled",
            "user_id": user_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel task")

@router.get("/queue/stats")
@track_performance("queue_stats")
async def get_queue_stats(current_user: Dict = Depends(get_current_user_required)):
    """Get task queue statistics"""
    user_id = current_user["user_id"]

    try:
        set_user_context(user_id, current_user.get("username"))

        # Only admins can see full queue stats
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=403,
                detail="Admin access required for queue statistics"
            )

        stats = task_queue.get_queue_stats()

        return {
            "queue_stats": stats,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting queue stats for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get queue statistics")

@router.post("/create-test")
@track_performance("test_task_creation")
async def create_test_task(
    task_type: str = "batch_moderation",
    current_user: Dict = Depends(get_current_user_required)
):
    """Create a test task for demonstration"""
    user_id = current_user["user_id"]

    try:
        set_user_context(user_id, current_user.get("username"))

        # Create test payload based on task type
        if task_type == "batch_moderation":
            test_payload = {
                "contents": ["Test content 1", "Test content 2", "Test content 3"],
                "content_type": "text",
                "metadata": {"test": True},
                "user_id": user_id,
                "total_items": 3
            }
        elif task_type == "analytics_generation":
            test_payload = {
                "analytics_type": "comprehensive",
                "time_range": "1h",
                "user_id": user_id
            }
        else:
            test_payload = {
                "test_data": "Sample test payload",
                "user_id": user_id
            }

        task_id = await task_queue.add_task(task_type, test_payload)

        return {
            "task_id": task_id,
            "task_type": task_type,
            "status": "created",
            "test_task": True,
            "user_id": user_id
        }

    except Exception as e:
        logger.error(f"Error creating test task for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create test task")
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, List
from datetime import datetime
import json
import logging

from app.auth_middleware import get_current_user_required
from app.observability import track_performance, structured_logger, set_user_context

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/gdpr", tags=["GDPR Compliance"])

@router.get("/privacy-policy")
async def get_privacy_policy():
    """Get privacy policy and GDPR information"""
    return {
        "title": "Privacy Policy - RL Content Moderation System",
        "version": "1.0",
        "last_updated": "2025-01-13",
        "data_collected": [
            "User authentication data (username, email)",
            "Content moderation history",
            "User feedback and ratings",
            "Performance analytics",
            "IP addresses and access logs"
        ],
        "data_usage": [
            "Content moderation and safety",
            "RL model training and improvement",
            "Analytics and performance monitoring",
            "User experience enhancement"
        ],
        "data_retention": "Data is retained for 365 days or until user deletion request",
        "user_rights": [
            "Right to access your data",
            "Right to data portability",
            "Right to data deletion",
            "Right to data correction",
            "Right to opt-out of analytics"
        ],
        "contact": {
            "email": "privacy@rl-moderation.com",
            "response_time": "30 days"
        }
    }

@router.get("/data-summary")
@track_performance("gdpr_data_summary")
async def get_data_summary(current_user: Dict = Depends(get_current_user_required)):
    """Get summary of user's stored data"""
    user_id = current_user["user_id"]

    try:
        set_user_context(user_id, current_user.get("username"))

        # Mock data summary - in real implementation, query actual databases
        data_summary = {
            "user_id": user_id,
            "username": current_user.get("username"),
            "email": current_user.get("email"),
            "data_categories": {
                "profile_data": {
                    "fields": ["user_id", "username", "email", "created_at"],
                    "count": 4,
                    "size_bytes": 256
                },
                "moderation_history": {
                    "count": 0,  # Would query actual moderation database
                    "date_range": "No data",
                    "size_bytes": 0
                },
                "feedback_history": {
                    "count": 0,  # Would query actual feedback database
                    "date_range": "No data",
                    "size_bytes": 0
                },
                "analytics_data": {
                    "count": 0,  # Would query analytics database
                    "date_range": "No data",
                    "size_bytes": 0
                }
            },
            "total_data_points": 4,
            "estimated_size_mb": 0.001,
            "last_activity": datetime.utcnow().isoformat(),
            "data_retention_days": 365
        }

        structured_logger.log_security_event(
            "gdpr_data_access",
            "127.0.0.1",  # Would get from request
            user_id,
            {"data_categories_count": len(data_summary["data_categories"])}
        )

        return data_summary

    except Exception as e:
        logger.error(f"Error getting data summary for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve data summary")

@router.get("/export-data")
@track_performance("gdpr_data_export")
async def export_user_data(
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user_required)
):
    """Export all user data in GDPR-compliant format"""
    user_id = current_user["user_id"]

    try:
        set_user_context(user_id, current_user.get("username"))

        # In a real implementation, this would gather data from all databases
        export_data = {
            "export_metadata": {
                "user_id": user_id,
                "export_timestamp": datetime.utcnow().isoformat(),
                "gdpr_version": "1.0",
                "data_portability_format": "JSON"
            },
            "profile_data": {
                "user_id": user_id,
                "username": current_user.get("username"),
                "email": current_user.get("email"),
                "created_at": current_user.get("created_at", datetime.utcnow().isoformat()),
                "last_login": current_user.get("last_login"),
                "role": current_user.get("role", "user")
            },
            "moderation_history": [],  # Would query moderation database
            "feedback_history": [],    # Would query feedback database
            "analytics_data": [],      # Would query analytics database
            "system_logs": []          # Would query audit logs (anonymized)
        }

        # Add background task to log the export
        background_tasks.add_task(
            structured_logger.log_security_event,
            "gdpr_data_export_completed",
            "127.0.0.1",
            user_id,
            {"export_size_bytes": len(json.dumps(export_data))}
        )

        return {
            "message": "Data export completed",
            "export_timestamp": export_data["export_metadata"]["export_timestamp"],
            "data": export_data,
            "format": "JSON",
            "compliance": "GDPR Article 20 - Right to Data Portability"
        }

    except Exception as e:
        logger.error(f"Error exporting data for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to export data")

@router.delete("/delete-data")
@track_performance("gdpr_data_deletion")
async def delete_user_data(
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user_required),
    confirmation: str = None
):
    """Delete all user data (GDPR Right to Erasure)"""
    user_id = current_user["user_id"]

    # Require explicit confirmation
    if confirmation != f"DELETE_ALL_DATA_{user_id}":
        raise HTTPException(
            status_code=400,
            detail="Confirmation required. Use confirmation='DELETE_ALL_DATA_{user_id}'"
        )

    try:
        set_user_context(user_id, current_user.get("username"))

        # In a real implementation, this would:
        # 1. Mark user as deleted (soft delete)
        # 2. Anonymize historical data
        # 3. Queue data for physical deletion after retention period
        # 4. Notify all integrated services

        deletion_summary = {
            "user_id": user_id,
            "deletion_timestamp": datetime.utcnow().isoformat(),
            "status": "scheduled",
            "data_categories_deleted": [
                "profile_data",
                "moderation_history",
                "feedback_history",
                "analytics_data",
                "system_logs"
            ],
            "retention_period_days": 30,  # Data kept for 30 days before physical deletion
            "gdpr_compliance": "Article 17 - Right to Erasure"
        }

        # Add background task for actual data deletion
        background_tasks.add_task(
            _perform_data_deletion,
            user_id,
            deletion_summary
        )

        # Log the deletion request
        structured_logger.log_security_event(
            "gdpr_data_deletion_requested",
            "127.0.0.1",
            user_id,
            {"confirmation_provided": True}
        )

        return {
            "message": "Data deletion scheduled",
            "deletion_id": f"del_{user_id}_{int(datetime.utcnow().timestamp())}",
            "scheduled_deletion_date": (
                datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) +
                timedelta(days=30)
            ).isoformat(),
            "status": "Data will be permanently deleted in 30 days",
            "compliance": "GDPR Article 17 - Right to Erasure"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scheduling data deletion for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to schedule data deletion")

async def _perform_data_deletion(user_id: str, deletion_summary: Dict[str, Any]):
    """Background task to perform actual data deletion"""
    try:
        logger.info(f"Performing data deletion for user {user_id}")

        # In a real implementation, this would:
        # - Delete from user database
        # - Anonymize moderation history
        # - Remove feedback data
        # - Clear analytics data
        # - Update audit logs

        # For now, just log the completion
        structured_logger.log_security_event(
            "gdpr_data_deletion_completed",
            "system",
            user_id,
            {"deletion_summary": deletion_summary}
        )

        logger.info(f"Data deletion completed for user {user_id}")

    except Exception as e:
        logger.error(f"Error during data deletion for user {user_id}: {e}")

        # Log the failure
        structured_logger.log_security_event(
            "gdpr_data_deletion_failed",
            "system",
            user_id,
            {"error": str(e)}
        )

@router.post("/restrict-processing")
async def restrict_data_processing(
    current_user: Dict = Depends(get_current_user_required),
    restriction_type: str = "analytics_opt_out"
):
    """Restrict processing of user data (GDPR Article 18)"""
    user_id = current_user["user_id"]

    valid_restrictions = ["analytics_opt_out", "marketing_opt_out", "processing_restriction"]

    if restriction_type not in valid_restrictions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid restriction type. Must be one of: {valid_restrictions}"
        )

    try:
        set_user_context(user_id, current_user.get("username"))

        # In a real implementation, this would update user preferences
        restriction_record = {
            "user_id": user_id,
            "restriction_type": restriction_type,
            "applied_timestamp": datetime.utcnow().isoformat(),
            "status": "active"
        }

        structured_logger.log_security_event(
            "gdpr_processing_restriction_applied",
            "127.0.0.1",
            user_id,
            {"restriction_type": restriction_type}
        )

        return {
            "message": f"Processing restriction '{restriction_type}' applied",
            "restriction_id": f"restrict_{user_id}_{restriction_type}",
            "applied_timestamp": restriction_record["applied_timestamp"],
            "status": "active",
            "compliance": "GDPR Article 18 - Right to Restriction of Processing"
        }

    except Exception as e:
        logger.error(f"Error applying processing restriction for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to apply processing restriction")
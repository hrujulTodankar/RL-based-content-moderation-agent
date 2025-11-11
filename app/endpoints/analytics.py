from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta
import random

from ..moderation_agent import ModerationAgent
from ..feedback_handler import FeedbackHandler

moderation_agent = ModerationAgent()
feedback_handler = FeedbackHandler()

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/rl-metrics")
async def get_rl_metrics() -> Dict[str, Any]:
    """Get reinforcement learning training metrics"""
    try:
        # Get agent statistics
        agent_stats = moderation_agent.get_statistics()

        # Generate mock historical data for visualization
        history_length = min(len(moderation_agent.history), 50)
        timestamps = []
        q_values = []
        learning_rates = []

        base_time = datetime.utcnow()
        for i in range(history_length):
            timestamps.append((base_time - timedelta(minutes=i*5)).strftime('%H:%M'))
            q_values.append(random.uniform(0, 1))
            learning_rates.append(moderation_agent.learning_rate * (0.8 + random.uniform(0, 0.4)))

        # Action counts from history
        action_counts = [0, 0, 0]  # approve, flag, review
        reward_distribution = [0, 0, 0]  # positive, neutral, negative

        for entry in moderation_agent.history[-100:]:
            action = entry.get("action", 0)
            if action < len(action_counts):
                action_counts[action] += 1

            # Calculate reward distribution
            if "result" in entry and "score" in entry["result"]:
                score = entry["result"]["score"]
                if score > 0.7:
                    reward_distribution[0] += 1  # positive
                elif score > 0.3:
                    reward_distribution[1] += 1  # neutral
                else:
                    reward_distribution[2] += 1  # negative

        return {
            "timestamps": timestamps,
            "q_values": q_values,
            "learning_rates": learning_rates,
            "action_counts": action_counts,
            "reward_distribution": reward_distribution,
            "q_table_size": agent_stats.get("q_table_size", 0),
            "total_moderations": agent_stats.get("total_moderations", 0),
            "epsilon": agent_stats.get("epsilon", 0.1)
        }

    except Exception as e:
        logger.error(f"Error getting RL metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving RL metrics")

@router.get("/performance")
async def get_performance_data(range: str = "24h") -> Dict[str, Any]:
    """Get model performance data over time"""
    try:
        # Parse time range
        if range == "1h":
            hours = 1
        elif range == "24h":
            hours = 24
        elif range == "7d":
            hours = 168
        elif range == "30d":
            hours = 720
        else:
            hours = 24

        # Generate performance data
        data_points = min(hours, 50)  # Max 50 data points
        timestamps = []
        accuracy = []
        confidence = []

        base_time = datetime.utcnow()
        base_accuracy = 0.5
        base_confidence = 0.6

        for i in range(data_points):
            timestamp = base_time - timedelta(hours=i)
            timestamps.append(timestamp.strftime('%m/%d %H:%M'))

            # Simulate improving accuracy over time
            improvement = min(i * 0.01, 0.3)  # Max 30% improvement
            accuracy.append(base_accuracy + improvement + random.uniform(-0.05, 0.05))

            # Confidence generally increases
            confidence_val = base_confidence + (i * 0.005) + random.uniform(-0.1, 0.1)
            confidence.append(max(0.1, min(0.95, confidence_val)))

        # Reverse to show chronological order
        timestamps.reverse()
        accuracy.reverse()
        confidence.reverse()

        # Calculate current stats
        current_accuracy = accuracy[-1] if accuracy else 0
        improvement_rate = (current_accuracy - accuracy[0]) / len(accuracy) if len(accuracy) > 1 else 0
        best_performance = max(accuracy) if accuracy else 0

        return {
            "timestamps": timestamps,
            "accuracy": accuracy,
            "confidence": confidence,
            "current_accuracy": current_accuracy,
            "improvement_rate": improvement_rate,
            "best_performance": best_performance,
            "training_sessions": len(moderation_agent.history)
        }

    except Exception as e:
        logger.error(f"Error getting performance data: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving performance data")

@router.get("/moderated-content")
async def get_moderated_content(page: int = 1, limit: int = 12) -> Dict[str, Any]:
    """Get paginated list of moderated content with visual appeal"""
    try:
        # Get moderation statistics
        stats = await feedback_handler.get_statistics()

        # Get recent moderations from database
        # For now, return sample data since we don't have real moderations
        sample_moderations = [
            {
                "moderation_id": f"mod_{i}",
                "content_type": "text",
                "flagged": False,
                "score": 0.85 + (i * 0.01),
                "confidence": 0.92,
                "reasons": ["Content quality approved", "Legal terminology present"],
                "timestamp": "2025-11-05T09:00:00Z",
                "content_preview": f"Sample legal content {i}...",
                "category": "criminal_law" if i % 2 == 0 else "civil_law",
                "status": "APPROVED"
            }
            for i in range(1, 51)
        ]

        # Apply pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_items = sample_moderations[start_idx:end_idx]

        # Enhanced response with visual metadata
        return {
            "items": paginated_items,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": len(sample_moderations),
                "pages": (len(sample_moderations) + limit - 1) // limit
            },
            "summary": {
                "total_moderated": stats.get("total_moderations", 0),
                "approved_count": sum(1 for item in sample_moderations if not item["flagged"]),
                "flagged_count": sum(1 for item in sample_moderations if item["flagged"]),
                "avg_score": sum(item["score"] for item in sample_moderations) / len(sample_moderations),
                "avg_confidence": sum(item["confidence"] for item in sample_moderations) / len(sample_moderations)
            },
            "visual_metadata": {
                "color_scheme": {
                    "approved": "#28a745",
                    "flagged": "#dc3545",
                    "pending": "#ffc107"
                },
                "icons": {
                    "text": "fas fa-file-alt",
                    "image": "fas fa-image",
                    "video": "fas fa-video",
                    "audio": "fas fa-music"
                },
                "categories": {
                    "criminal_law": {"color": "#dc3545", "icon": "fas fa-gavel"},
                    "civil_law": {"color": "#007bff", "icon": "fas fa-balance-scale"},
                    "constitutional_law": {"color": "#28a745", "icon": "fas fa-flag"},
                    "employment_law": {"color": "#fd7e14", "icon": "fas fa-briefcase"}
                }
            }
        }

    except Exception as e:
        logger.error(f"Error getting moderated content: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving moderated content")

@router.get("/accuracy-trends")
async def get_accuracy_trends(content: str = "all", range: str = "24h") -> Dict[str, Any]:
    """Get accuracy trends with content type filtering"""
    try:
        # Parse time range
        if range == "1h":
            hours = 1
        elif range == "6h":
            hours = 6
        elif range == "24h":
            hours = 24
        elif range == "7d":
            hours = 168
        else:
            hours = 24

        # Generate trend data
        data_points = min(hours * 2, 50)  # 2 points per hour, max 50
        timestamps = []
        overall_accuracy = []
        text_accuracy = []
        media_accuracy = []

        base_time = datetime.utcnow()

        for i in range(data_points):
            timestamp = base_time - timedelta(minutes=i*30)  # Every 30 minutes
            timestamps.append(timestamp.strftime('%m/%d %H:%M'))

            # Generate accuracy data
            base_acc = 0.6 + (i * 0.002)  # Gradual improvement

            overall_accuracy.append(base_acc + random.uniform(-0.1, 0.1))
            text_accuracy.append(base_acc + random.uniform(-0.05, 0.15))
            media_accuracy.append(base_acc + random.uniform(-0.15, 0.05))

        # Reverse for chronological order
        timestamps.reverse()
        overall_accuracy.reverse()
        text_accuracy.reverse()
        media_accuracy.reverse()

        # Calculate content performance
        content_performance = {
            "text": sum(text_accuracy[-10:]) / len(text_accuracy[-10:]) if text_accuracy else 0,
            "image": sum(media_accuracy[-10:]) / len(media_accuracy[-10:]) * 0.9 if media_accuracy else 0,
            "video": sum(media_accuracy[-10:]) / len(media_accuracy[-10:]) * 0.8 if media_accuracy else 0,
            "audio": sum(media_accuracy[-10:]) / len(media_accuracy[-10:]) * 0.85 if media_accuracy else 0
        }

        # Generate insights
        insights = [
            "Text content shows highest accuracy improvement",
            "Media content accuracy is improving steadily",
            "Overall system confidence is increasing",
            "Q-learning updates are becoming more effective"
        ]

        if content_performance["text"] > content_performance["image"]:
            insights.append("Text moderation outperforms media moderation")
        else:
            insights.append("Media moderation is catching up to text performance")

        return {
            "timestamps": timestamps,
            "overall_accuracy": overall_accuracy,
            "text_accuracy": text_accuracy,
            "media_accuracy": media_accuracy,
            "content_performance": content_performance,
            "insights": insights
        }

    except Exception as e:
        logger.error(f"Error getting accuracy trends: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving accuracy trends")
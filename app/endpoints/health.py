from fastapi import APIRouter
from datetime import datetime
from app.observability import (
    performance_monitor, get_observability_health,
    sentry_manager, posthog_manager
)
from app.moderation_agent import moderation_agent

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
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

@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with observability status"""
    observability_health = get_observability_health()

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": performance_monitor.get_uptime(),
        "services": {
            "moderation_agent": "running",
            "feedback_handler": "running",
            "event_queue": "running",
            "mcp_integrator": "running"
        },
        "observability": observability_health,
        "performance": {
            "total_operations": len(performance_monitor.metrics),
            "slow_operations_count": len(performance_monitor.slow_operations)
        },
        "rl_agent": moderation_agent.get_statistics() if moderation_agent else None
    }

@router.get("/observability/health")
async def observability_health():
    """Check observability services health"""
    return get_observability_health()

@router.get("/metrics")
async def get_metrics():
    """Get basic performance metrics"""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": performance_monitor.get_uptime(),
        "performance_summary": performance_monitor.get_performance_summary(),
        "rl_agent_stats": moderation_agent.get_statistics() if moderation_agent else None
    }

@router.get("/metrics/performance")
async def performance_metrics():
    """Detailed performance metrics"""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": performance_monitor.get_uptime(),
        "performance_summary": performance_monitor.get_performance_summary(),
        "recent_slow_operations": performance_monitor.slow_operations[-10:] if performance_monitor.slow_operations else []
    }

@router.get("/monitoring-status")
async def monitoring_status():
    """Get monitoring system status"""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "sentry_enabled": sentry_manager.initialized,
        "posthog_enabled": posthog_manager.initialized,
        "performance_monitoring_enabled": True,
        "uptime_seconds": performance_monitor.get_uptime(),
        "total_metrics_collected": len(performance_monitor.metrics),
        "slow_operations_count": len(performance_monitor.slow_operations)
    }

@router.get("/")
async def root():
    return {
        "message": "RL-Powered Content Moderation API",
        "version": "2.0",
        "status": "running",
        "observability_enabled": sentry_manager.initialized or posthog_manager.initialized
    }
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/health")
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

@router.get("/")
async def root():
    return {
        "message": "RL-Powered Content Moderation API",
        "version": "2.0",
        "status": "running"
    }
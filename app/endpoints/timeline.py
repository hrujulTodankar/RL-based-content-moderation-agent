from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta, timezone, date

logger = logging.getLogger(__name__)

router = APIRouter()

class TimelineRequest(BaseModel):
    case_id: str
    case_type: str
    jurisdiction: str = "IN"
    start_date: str = None

class TimelineResponse(BaseModel):
    case_id: str
    timeline_events: List[Dict[str, Any]]
    estimated_completion: str
    critical_deadlines: List[Dict[str, Any]]
    next_actions: List[Dict[str, Any]]

# Mock timeline data for different case types
CASE_TIMELINES = {
    "criminal": {
        "events": [
            {"stage": "FIR Registration", "duration": 1, "description": "First Information Report filed"},
            {"stage": "Investigation", "duration": 30, "description": "Police investigation and evidence collection"},
            {"stage": "Charge Sheet", "duration": 60, "description": "Filing of charge sheet by police"},
            {"stage": "Trial", "duration": 180, "description": "Court proceedings and trial"},
            {"stage": "Judgment", "duration": 90, "description": "Final court judgment"}
        ],
        "critical_deadlines": [
            {"event": "Investigation completion", "days_from_start": 60, "importance": "high"},
            {"event": "Charge sheet filing", "days_from_start": 90, "importance": "high"},
            {"event": "Trial completion target", "days_from_start": 365, "importance": "medium"}
        ]
    },
    "civil": {
        "events": [
            {"stage": "Plaint Filing", "duration": 1, "description": "Filing of civil suit"},
            {"stage": "Summons", "duration": 15, "description": "Service of summons to defendant"},
            {"stage": "Written Statement", "duration": 30, "description": "Defendant's response filing"},
            {"stage": "Evidence & Arguments", "duration": 120, "description": "Evidence presentation and arguments"},
            {"stage": "Judgment", "duration": 60, "description": "Final court judgment"}
        ],
        "critical_deadlines": [
            {"event": "Written statement filing", "days_from_start": 30, "importance": "high"},
            {"event": "Evidence completion", "days_from_start": 180, "importance": "medium"},
            {"event": "Final arguments", "days_from_start": 240, "importance": "high"}
        ]
    }
}

@router.post("/timeline")
async def generate_timeline(request: TimelineRequest):
    """
    Simple timeline generation for legal cases
    """
    # Return a simple response that matches the frontend expectations
    return {
        "case_id": request.case_id,
        "timeline_events": [
            {
                "stage": "Case Filing",
                "date": "2024-01-15",
                "description": "Initial case filing and documentation",
                "duration_days": 15,
                "status": "upcoming"
            },
            {
                "stage": "Evidence Collection",
                "date": "2024-02-15",
                "description": "Gather and organize all evidence",
                "duration_days": 30,
                "status": "upcoming"
            }
        ],
        "estimated_completion": "2024-02-15",
        "critical_deadlines": [],
        "next_actions": []
    }
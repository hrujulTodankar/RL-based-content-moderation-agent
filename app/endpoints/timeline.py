from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta

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

@router.post("/timeline", response_model=TimelineResponse)
async def generate_timeline(request: TimelineRequest):
    """
    Dynamic timeline generation for legal cases
    """
    try:
        case_type = request.case_type.lower()

        if case_type not in CASE_TIMELINES:
            raise HTTPException(status_code=400, detail=f"Unsupported case type: {case_type}")

        timeline_data = CASE_TIMELINES[case_type]

        # Calculate start date
        if request.start_date:
            try:
                start_date = datetime.fromisoformat(request.start_date.replace('Z', '+00:00'))
                # Convert to timezone-naive if it's timezone-aware
                if start_date.tzinfo is not None:
                    start_date = start_date.replace(tzinfo=None)
            except:
                start_date = datetime.now()
        else:
            start_date = datetime.now()

        # Generate timeline events
        timeline_events = []
        current_date = start_date

        for event in timeline_data["events"]:
            event_date = current_date + timedelta(days=event["duration"])
            timeline_events.append({
                "stage": event["stage"],
                "date": event_date.strftime("%Y-%m-%d"),
                "description": event["description"],
                "duration_days": event["duration"],
                "status": "upcoming"
            })
            current_date = event_date

        # Calculate estimated completion
        total_days = sum(event["duration"] for event in timeline_data["events"])
        completion_date = start_date + timedelta(days=total_days)
        estimated_completion = completion_date.strftime("%Y-%m-%d")

        # Generate critical deadlines
        critical_deadlines = []
        for deadline in timeline_data["critical_deadlines"]:
            deadline_date = start_date + timedelta(days=deadline["days_from_start"])
            critical_deadlines.append({
                "event": deadline["event"],
                "date": deadline_date.strftime("%Y-%m-%d"),
                "days_remaining": (deadline_date - datetime.now()).days,
                "importance": deadline["importance"]
            })

        # Next actions based on current stage
        next_actions = []
        if timeline_events:
            next_event = timeline_events[0]
            days_until_next = (datetime.fromisoformat(next_event["date"]) - datetime.now()).days

            next_actions.append({
                "action": f"Prepare for {next_event['stage']}",
                "deadline": next_event["date"],
                "days_remaining": max(0, days_until_next),
                "priority": "high"
            })

            if len(timeline_events) > 1:
                next_actions.append({
                    "action": f"Plan {timeline_events[1]['stage']} preparation",
                    "deadline": timeline_events[1]["date"],
                    "days_remaining": (datetime.fromisoformat(timeline_events[1]["date"]) - datetime.now()).days,
                    "priority": "medium"
                })

        return TimelineResponse(
            case_id=request.case_id,
            timeline_events=timeline_events,
            estimated_completion=estimated_completion,
            critical_deadlines=critical_deadlines,
            next_actions=next_actions
        )

    except Exception as e:
        logger.error(f"Timeline generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Timeline generation failed")
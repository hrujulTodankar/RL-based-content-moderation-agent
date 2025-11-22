from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta, timezone, date
from enum import Enum

logger = logging.getLogger(__name__)

router = APIRouter()

class JurisdictionEnum(str, Enum):
    IN = "IN"  # India
    US = "US"  # United States
    UK = "UK"  # United Kingdom
    CA = "CA"  # Canada
    AU = "AU"  # Australia
    EU = "EU"  # European Union

class PriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class CaseSeverityEnum(str, Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"

class TimelineRequest(BaseModel):
    case_id: str
    case_type: str
    jurisdiction: JurisdictionEnum = Field(default=JurisdictionEnum.IN, description="Jurisdiction/country code")
    start_date: Optional[str] = Field(default=None, description="Start date in YYYY-MM-DD format")
    priority: PriorityEnum = Field(default=PriorityEnum.MEDIUM, description="Case priority level")
    case_severity: CaseSeverityEnum = Field(default=CaseSeverityEnum.MODERATE, description="Severity level affecting timeline calculations")

class TimelineResponse(BaseModel):
    case_id: str
    timeline_events: List[Dict[str, Any]]
    estimated_completion: str
    critical_deadlines: List[Dict[str, Any]]
    next_actions: List[Dict[str, Any]]

# Mock timeline data for different case types and jurisdictions
CASE_TIMELINES = {
    "criminal": {
        "IN": {
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
        "US": {
            "events": [
                {"stage": "Arrest & Booking", "duration": 1, "description": "Arrest and initial booking"},
                {"stage": "Initial Appearance", "duration": 3, "description": "First court appearance"},
                {"stage": "Preliminary Hearing", "duration": 30, "description": "Evidence review and charges"},
                {"stage": "Trial", "duration": 120, "description": "Court proceedings"},
                {"stage": "Sentencing", "duration": 30, "description": "Final sentencing"}
            ],
            "critical_deadlines": [
                {"event": "Preliminary hearing", "days_from_start": 45, "importance": "high"},
                {"event": "Trial start", "days_from_start": 120, "importance": "high"},
                {"event": "Sentencing", "days_from_start": 180, "importance": "medium"}
            ]
        },
        "UK": {
            "events": [
                {"stage": "Charge", "duration": 1, "description": "Formal charges filed"},
                {"stage": "First Hearing", "duration": 7, "description": "Magistrates court first hearing"},
                {"stage": "Committal", "duration": 28, "description": "Transfer to crown court"},
                {"stage": "Crown Court Trial", "duration": 90, "description": "Crown court proceedings"},
                {"stage": "Sentencing", "duration": 14, "description": "Final sentencing"}
            ],
            "critical_deadlines": [
                {"event": "Committal to crown court", "days_from_start": 35, "importance": "high"},
                {"event": "Trial preparation", "days_from_start": 90, "importance": "high"},
                {"event": "Sentencing", "days_from_start": 120, "importance": "medium"}
            ]
        }
    },
    "civil": {
        "IN": {
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
        },
        "US": {
            "events": [
                {"stage": "Complaint Filing", "duration": 1, "description": "Civil complaint filed"},
                {"stage": "Service of Process", "duration": 30, "description": "Defendant served with summons"},
                {"stage": "Answer Filing", "duration": 20, "description": "Defendant's answer to complaint"},
                {"stage": "Discovery", "duration": 180, "description": "Information gathering phase"},
                {"stage": "Trial", "duration": 60, "description": "Court proceedings"}
            ],
            "critical_deadlines": [
                {"event": "Service of process", "days_from_start": 30, "importance": "high"},
                {"event": "Discovery completion", "days_from_start": 210, "importance": "high"},
                {"event": "Pre-trial motions", "days_from_start": 270, "importance": "medium"}
            ]
        }
    }
}

def calculate_priority_modifier(priority: PriorityEnum) -> float:
    """Calculate duration modifier based on priority level"""
    modifiers = {
        PriorityEnum.LOW: 1.2,     # 20% longer for low priority
        PriorityEnum.MEDIUM: 1.0,   # Normal duration
        PriorityEnum.HIGH: 0.8      # 20% shorter for high priority
    }
    return modifiers[priority]

def calculate_severity_modifier(case_severity: CaseSeverityEnum) -> float:
    """Calculate duration modifier based on case severity"""
    modifiers = {
        CaseSeverityEnum.MINOR: 0.9,      # 10% shorter
        CaseSeverityEnum.MODERATE: 1.0,   # Normal duration
        CaseSeverityEnum.SEVERE: 1.3,     # 30% longer
        CaseSeverityEnum.CRITICAL: 0.7    # 30% shorter for critical cases
    }
    return modifiers[case_severity]

def calculate_start_date(start_date_str: Optional[str]) -> date:
    """Calculate the start date, defaulting to today if not provided"""
    if start_date_str:
        try:
            return datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except ValueError:
            logger.warning(f"Invalid start date format: {start_date_str}, using today")
    
    return datetime.now(timezone.utc).date()

@router.post("/timeline")
async def generate_timeline(request: TimelineRequest):
    """
    Enhanced timeline generation for legal cases with jurisdiction, priority, and severity support
    """
    try:
        # Get timeline data for the specific jurisdiction and case type
        if request.case_type not in CASE_TIMELINES:
            raise HTTPException(status_code=400, detail=f"Unsupported case type: {request.case_type}")
        
        if request.jurisdiction.value not in CASE_TIMELINES[request.case_type]:
            raise HTTPException(status_code=400, 
                              detail=f"Jurisdiction {request.jurisdiction.value} not supported for case type {request.case_type}")
        
        timeline_data = CASE_TIMELINES[request.case_type][request.jurisdiction.value]
        
        # Calculate duration modifiers
        priority_modifier = calculate_priority_modifier(request.priority)
        severity_modifier = calculate_severity_modifier(request.case_severity)
        combined_modifier = priority_modifier * severity_modifier
        
        # Calculate start date
        start_date = calculate_start_date(request.start_date)
        
        # Generate timeline events
        timeline_events = []
        current_date = start_date
        
        for event in timeline_data["events"]:
            # Apply duration modifiers
            base_duration = event["duration"]
            adjusted_duration = int(base_duration * combined_modifier)
            
            # Ensure minimum duration of 1 day
            adjusted_duration = max(1, adjusted_duration)
            
            # Calculate event date
            event_date = current_date + timedelta(days=adjusted_duration)
            
            timeline_event = {
                "stage": event["stage"],
                "date": event_date.strftime("%Y-%m-%d"),
                "description": event["description"],
                "duration_days": adjusted_duration,
                "status": "upcoming",
                "base_duration": base_duration,
                "adjusted_for": {
                    "priority": f"{request.priority.value} (x{priority_modifier})",
                    "severity": f"{request.case_severity.value} (x{severity_modifier})"
                }
            }
            
            timeline_events.append(timeline_event)
            current_date = event_date
        
        # Generate critical deadlines
        critical_deadlines = []
        for deadline in timeline_data["critical_deadlines"]:
            # Apply modifiers to critical deadlines
            base_days = deadline["days_from_start"]
            adjusted_days = int(base_days * combined_modifier)
            adjusted_days = max(1, adjusted_days)
            
            deadline_date = start_date + timedelta(days=adjusted_days)
            
            critical_deadline = {
                "event": deadline["event"],
                "date": deadline_date.strftime("%Y-%m-%d"),
                "days_from_start": adjusted_days,
                "importance": deadline["importance"],
                "base_days": base_days,
                "adjusted_for": f"priority + severity (x{combined_modifier})"
            }
            critical_deadlines.append(critical_deadline)
        
        # Calculate estimated completion
        estimated_completion = current_date.strftime("%Y-%m-%d")
        
        # Generate next actions based on parameters
        next_actions = [
            {
                "action": "File initial documents",
                "priority": "high" if request.priority == PriorityEnum.HIGH else "medium",
                "timeline": "Immediate"
            },
            {
                "action": "Gather evidence",
                "priority": "high" if request.case_severity == CaseSeverityEnum.CRITICAL else "medium",
                "timeline": "Within 2 weeks"
            }
        ]
        
        if request.priority == PriorityEnum.HIGH:
            next_actions.append({
                "action": "Expedite proceedings",
                "priority": "high",
                "timeline": "As soon as possible"
            })
        
        if request.case_severity == CaseSeverityEnum.CRITICAL:
            next_actions.append({
                "action": "Assign senior counsel",
                "priority": "critical",
                "timeline": "Immediately"
            })
        
        return {
            "case_id": request.case_id,
            "jurisdiction": request.jurisdiction.value,
            "case_type": request.case_type,
            "priority": request.priority.value,
            "case_severity": request.case_severity.value,
            "timeline_events": timeline_events,
            "estimated_completion": estimated_completion,
            "critical_deadlines": critical_deadlines,
            "next_actions": next_actions,
            "calculation_modifiers": {
                "priority_modifier": priority_modifier,
                "severity_modifier": severity_modifier,
                "combined_modifier": combined_modifier,
                "start_date": start_date.strftime("%Y-%m-%d")
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating timeline: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error generating timeline")
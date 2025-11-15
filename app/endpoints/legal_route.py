from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class LegalRouteRequest(BaseModel):
    case_description: str
    case_type: str
    jurisdiction: str = "IN"
    urgency_level: str = "normal"

class LegalRouteResponse(BaseModel):
    recommended_route: str
    court_hierarchy: List[Dict[str, Any]]
    estimated_timeline: str
    success_probability: float
    alternative_routes: List[Dict[str, Any]]
    required_documents: List[str]
    cost_estimate: Dict[str, Any]

# Mock legal route data
LEGAL_ROUTES = {
    "criminal": {
        "routes": [
            {
                "court": "Supreme Court",
                "conditions": ["constitutional issues", "death penalty", "national importance"],
                "timeline": "2-5 years",
                "success_rate": 0.15
            },
            {
                "court": "High Court",
                "conditions": ["serious offenses", "judicial review", "state-wide impact"],
                "timeline": "1-3 years",
                "success_rate": 0.35
            },
            {
                "court": "Sessions Court",
                "conditions": ["most criminal cases", "felony charges"],
                "timeline": "6-18 months",
                "success_rate": 0.60
            },
            {
                "court": "Magistrate Court",
                "conditions": ["minor offenses", "summary trials"],
                "timeline": "3-6 months",
                "success_rate": 0.75
            }
        ]
    },
    "civil": {
        "routes": [
            {
                "court": "Supreme Court",
                "conditions": ["constitutional matters", "inter-state disputes"],
                "timeline": "2-4 years",
                "success_rate": 0.20
            },
            {
                "court": "High Court",
                "conditions": ["complex civil matters", "company law", "intellectual property"],
                "timeline": "1-2 years",
                "success_rate": 0.45
            },
            {
                "court": "District Court",
                "conditions": ["general civil disputes", "contract matters", "property disputes"],
                "timeline": "8-15 months",
                "success_rate": 0.65
            },
            {
                "court": "Small Causes Court",
                "conditions": ["minor claims", "rent disputes", "up to ₹20,000"],
                "timeline": "3-8 months",
                "success_rate": 0.70
            }
        ]
    }
}

@router.post("/legal-route", response_model=LegalRouteResponse)
async def get_legal_route(request: LegalRouteRequest):
    """
    Case-driven legal route recommendation system
    """
    try:
        case_type = request.case_type.lower()
        case_desc = request.case_description.lower()

        if case_type not in LEGAL_ROUTES:
            raise HTTPException(status_code=400, detail=f"Unsupported case type: {case_type}")

        routes = LEGAL_ROUTES[case_type]["routes"]

        # Determine recommended route based on case description
        recommended_route = None
        max_score = 0

        for route in routes:
            score = 0
            for condition in route["conditions"]:
                if any(word in case_desc for word in condition.split()):
                    score += 1
            if score > max_score:
                max_score = score
                recommended_route = route

        if not recommended_route:
            recommended_route = routes[-1]  # Default to lowest court

        # Build court hierarchy
        court_hierarchy = []
        for i, route in enumerate(routes):
            court_hierarchy.append({
                "level": i + 1,
                "court": route["court"],
                "recommended": route["court"] == recommended_route["court"],
                "timeline": route["timeline"],
                "success_rate": route["success_rate"]
            })

        # Alternative routes
        alternative_routes = [
            {
                "court": route["court"],
                "timeline": route["timeline"],
                "success_rate": route["success_rate"],
                "reason": f"Alternative path for {case_type} cases"
            }
            for route in routes if route["court"] != recommended_route["court"]
        ][:2]

        # Required documents based on case type
        base_documents = ["Case filing application", "Court fee payment", "Identity proof"]
        if case_type == "criminal":
            required_documents = base_documents + [
                "FIR copy", "Charge sheet", "Witness statements",
                "Medical reports", "Evidence documents"
            ]
        else:
            required_documents = base_documents + [
                "Plaint document", "Supporting affidavits",
                "Property documents", "Contract copies"
            ]

        # Cost estimate
        cost_estimate = {
            "court_fee": "₹500 - ₹50,000",
            "advocate_fee": "₹10,000 - ₹2,00,000",
            "miscellaneous": "₹5,000 - ₹25,000",
            "total_range": "₹15,500 - ₹2,75,000"
        }

        return LegalRouteResponse(
            recommended_route=recommended_route["court"],
            court_hierarchy=court_hierarchy,
            estimated_timeline=recommended_route["timeline"],
            success_probability=recommended_route["success_rate"],
            alternative_routes=alternative_routes,
            required_documents=required_documents,
            cost_estimate=cost_estimate
        )

    except Exception as e:
        logger.error(f"Legal route error: {str(e)}")
        raise HTTPException(status_code=500, detail="Legal route calculation failed")
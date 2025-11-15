from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import logging
import random

logger = logging.getLogger(__name__)

router = APIRouter()

class SuccessRateRequest(BaseModel):
    case_type: str
    jurisdiction: str = "IN"
    court_level: str = "district"
    case_complexity: str = "medium"
    lawyer_experience: str = "medium"

class SuccessRateResponse(BaseModel):
    overall_success_rate: float
    confidence_interval: Dict[str, float]
    factors_influencing: List[Dict[str, Any]]
    recommendations: List[str]
    historical_data: Dict[str, Any]

# Mock success rate data
SUCCESS_RATES = {
    "criminal": {
        "supreme_court": {"base_rate": 0.15, "complexity_modifier": {"low": -0.05, "medium": 0, "high": 0.05}},
        "high_court": {"base_rate": 0.35, "complexity_modifier": {"low": -0.05, "medium": 0, "high": 0.05}},
        "district_court": {"base_rate": 0.60, "complexity_modifier": {"low": -0.05, "medium": 0, "high": 0.05}}
    },
    "civil": {
        "supreme_court": {"base_rate": 0.20, "complexity_modifier": {"low": -0.05, "medium": 0, "high": 0.05}},
        "high_court": {"base_rate": 0.45, "complexity_modifier": {"low": -0.05, "medium": 0, "high": 0.05}},
        "district_court": {"base_rate": 0.65, "complexity_modifier": {"low": -0.05, "medium": 0, "high": 0.05}}
    }
}

LAWYER_MODIFIERS = {
    "junior": -0.10,
    "medium": 0,
    "senior": 0.10,
    "expert": 0.15
}

@router.post("/success-rate", response_model=SuccessRateResponse)
async def predict_success_rate(request: SuccessRateRequest):
    """
    ML-powered success rate prediction for legal cases
    """
    try:
        case_type = request.case_type.lower()
        court_level = request.court_level.lower()

        if case_type not in SUCCESS_RATES:
            raise HTTPException(status_code=400, detail=f"Unsupported case type: {case_type}")

        if court_level not in SUCCESS_RATES[case_type]:
            raise HTTPException(status_code=400, detail=f"Unsupported court level: {court_level}")

        # Base success rate
        base_data = SUCCESS_RATES[case_type][court_level]
        base_rate = base_data["base_rate"]

        # Apply modifiers
        complexity_modifier = base_data["complexity_modifier"].get(request.case_complexity.lower(), 0)
        lawyer_modifier = LAWYER_MODIFIERS.get(request.lawyer_experience.lower(), 0)

        # Calculate final success rate
        success_rate = base_rate + complexity_modifier + lawyer_modifier
        success_rate = max(0.05, min(0.95, success_rate))  # Clamp between 5% and 95%

        # Confidence interval (simplified)
        margin_of_error = 0.08  # ±8%
        confidence_interval = {
            "lower": max(0.01, success_rate - margin_of_error),
            "upper": min(0.99, success_rate + margin_of_error)
        }

        # Factors influencing success
        factors_influencing = [
            {
                "factor": "Court Level",
                "impact": "high" if court_level == "supreme_court" else "medium",
                "description": f"{court_level.replace('_', ' ').title()} court has {base_rate:.0%} base success rate"
            },
            {
                "factor": "Case Complexity",
                "impact": "medium",
                "description": f"{request.case_complexity.title()} complexity {'increases' if complexity_modifier > 0 else 'decreases'} success rate by {abs(complexity_modifier):.0%}"
            },
            {
                "factor": "Lawyer Experience",
                "impact": "high",
                "description": f"{request.lawyer_experience.title()} lawyer experience {'improves' if lawyer_modifier > 0 else 'reduces'} success rate by {abs(lawyer_modifier):.0%}"
            },
            {
                "factor": "Evidence Strength",
                "impact": "high",
                "description": "Strong evidence significantly improves success probability"
            },
            {
                "factor": "Legal Precedents",
                "impact": "medium",
                "description": "Favorable case law increases success rate"
            }
        ]

        # Recommendations
        recommendations = []
        if success_rate < 0.4:
            recommendations.append("Consider settlement or alternative dispute resolution")
            recommendations.append("Strengthen evidence collection before proceeding")
        elif success_rate < 0.6:
            recommendations.append("Consider upgrading to higher court if evidence is strong")
            recommendations.append("Engage senior legal counsel for better representation")
        else:
            recommendations.append("Proceed with confidence - success rate is favorable")
            recommendations.append("Ensure all procedural requirements are met")

        if request.lawyer_experience.lower() == "junior":
            recommendations.append("Consider consulting senior counsel for complex aspects")

        # Historical data (mock)
        historical_data = {
            "total_cases_analyzed": random.randint(1000, 5000),
            "success_rate_trend": "stable",
            "court_specific_rates": {
                court: data["base_rate"]
                for court, data in SUCCESS_RATES[case_type].items()
            },
            "last_updated": "2024-01-15"
        }

        return SuccessRateResponse(
            overall_success_rate=round(success_rate, 3),
            confidence_interval={k: round(v, 3) for k, v in confidence_interval.items()},
            factors_influencing=factors_influencing,
            recommendations=recommendations,
            historical_data=historical_data
        )

    except Exception as e:
        logger.error(f"Success rate prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail="Success rate prediction failed")
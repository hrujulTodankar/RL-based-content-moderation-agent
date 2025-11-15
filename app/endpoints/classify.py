from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ClassificationRequest(BaseModel):
    text: str
    domain_hints: List[str] = []

class ClassificationResponse(BaseModel):
    primary_domain: str
    confidence: float
    secondary_domains: List[Dict[str, Any]]
    legal_relevance: float
    risk_score: float

# Mock ML classification data
LEGAL_DOMAINS = {
    "criminal_law": ["crime", "offense", "punishment", "arrest", "bail", "warrant"],
    "civil_law": ["contract", "property", "tort", "damages", "liability"],
    "constitutional_law": ["fundamental rights", "constitution", "supreme court", "high court"],
    "corporate_law": ["company", "incorporation", "board", "shareholder", "merger"],
    "family_law": ["marriage", "divorce", "custody", "adoption", "maintenance"],
    "property_law": ["land", "ownership", "lease", "mortgage", "easement"],
    "labor_law": ["employment", "wage", "union", "termination", "discrimination"],
    "tax_law": ["income tax", "gst", "customs", "excise", "assessment"]
}

@router.post("/classify", response_model=ClassificationResponse)
async def classify_text(request: ClassificationRequest):
    """
    ML-powered domain classification for legal text
    """
    try:
        text_lower = request.text.lower()

        # Calculate domain scores
        domain_scores = {}
        for domain, keywords in LEGAL_DOMAINS.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                domain_scores[domain] = score

        if not domain_scores:
            # Default classification
            primary_domain = "general_law"
            confidence = 0.3
        else:
            # Find primary domain
            primary_domain = max(domain_scores, key=domain_scores.get)
            max_score = domain_scores[primary_domain]
            total_keywords = sum(len(keywords) for keywords in LEGAL_DOMAINS.values())
            confidence = min(max_score / 5.0, 0.95)  # Normalize confidence

        # Secondary domains
        secondary_domains = [
            {"domain": domain, "score": score, "confidence": min(score / 3.0, 0.8)}
            for domain, score in sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)[1:4]
        ]

        # Legal relevance and risk assessment
        legal_keywords = sum(len(keywords) for keywords in LEGAL_DOMAINS.values())
        legal_matches = sum(1 for keywords in LEGAL_DOMAINS.values()
                          for keyword in keywords if keyword in text_lower)
        legal_relevance = min(legal_matches / legal_keywords, 1.0)

        # Risk score based on sensitive keywords
        risk_keywords = ["violence", "harm", "illegal", "penalty", "punishment", "criminal"]
        risk_score = sum(1 for keyword in risk_keywords if keyword in text_lower) / len(risk_keywords)

        return ClassificationResponse(
            primary_domain=primary_domain.replace("_", " ").title(),
            confidence=round(confidence, 3),
            secondary_domains=secondary_domains,
            legal_relevance=round(legal_relevance, 3),
            risk_score=round(risk_score, 3)
        )

    except Exception as e:
        logger.error(f"Classification error: {str(e)}")
        raise HTTPException(status_code=500, detail="Classification failed")
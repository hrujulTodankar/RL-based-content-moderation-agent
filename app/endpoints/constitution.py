from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ConstitutionRequest(BaseModel):
    query: str
    jurisdiction: str = "IN"
    article_number: Optional[int] = None

class ConstitutionResponse(BaseModel):
    articles: List[Dict[str, Any]]
    relevant_sections: List[Dict[str, Any]]
    interpretation: str
    case_law: List[Dict[str, Any]]
    amendments: List[Dict[str, Any]]

# Mock Indian Constitution data
INDIAN_CONSTITUTION = {
    "fundamental_rights": {
        "articles": [
            {
                "number": 14,
                "title": "Right to Equality",
                "content": "The State shall not deny to any person equality before the law or the equal protection of the laws within the territory of India.",
                "key_cases": ["Kesavananda Bharati v. State of Kerala", "Maneka Gandhi v. Union of India"]
            },
            {
                "number": 19,
                "title": "Protection of certain rights regarding freedom of speech",
                "content": "All citizens shall have the right to freedom of speech and expression.",
                "key_cases": ["Shreya Singhal v. Union of India", "K.A. Abbas v. Union of India"]
            },
            {
                "number": 21,
                "title": "Protection of life and personal liberty",
                "content": "No person shall be deprived of his life or personal liberty except according to procedure established by law.",
                "key_cases": ["Maneka Gandhi v. Union of India", "Gautam Navlakha v. NIA"]
            }
        ]
    },
    "directive_principles": {
        "articles": [
            {
                "number": 39,
                "title": "Certain principles of policy to be followed by the State",
                "content": "The State shall, in particular, direct its policy towards securing that the citizens, men and women equally, have the right to an adequate means of livelihood.",
                "key_cases": ["State of Kerala v. N.M. Thomas", "Unni Krishnan v. State of Andhra Pradesh"]
            }
        ]
    },
    "fundamental_duties": {
        "articles": [
            {
                "number": 51A,
                "title": "Fundamental Duties",
                "content": "It shall be the duty of every citizen of India to abide by the Constitution and respect its ideals and institutions.",
                "key_cases": ["AIIMS Students Union v. AIIMS", "Navneet Kumar Gupta v. Union of India"]
            }
        ]
    }
}

@router.post("/constitution", response_model=ConstitutionResponse)
async def search_constitution(request: ConstitutionRequest):
    """
    Constitution article mapping and interpretation
    """
    try:
        query_lower = request.query.lower()
        jurisdiction = request.jurisdiction.upper()

        if jurisdiction != "IN":
            raise HTTPException(status_code=400, detail=f"Jurisdiction {jurisdiction} not supported yet")

        # If specific article requested
        if request.article_number:
            for category, data in INDIAN_CONSTITUTION.items():
                for article in data["articles"]:
                    if article["number"] == request.article_number:
                        return ConstitutionResponse(
                            articles=[article],
                            relevant_sections=[],
                            interpretation=f"Article {article['number']} - {article['title']}: {article['content'][:100]}...",
                            case_law=[{"case": case, "year": "2023", "court": "Supreme Court"} for case in article["key_cases"]],
                            amendments=[]
                        )

        # Search by content/query
        matching_articles = []
        for category, data in INDIAN_CONSTITUTION.items():
            for article in data["articles"]:
                if (str(article["number"]) in request.query or
                    any(word in article["title"].lower() for word in query_lower.split()) or
                    any(word in article["content"].lower() for word in query_lower.split())):
                    matching_articles.append(article)

        if not matching_articles:
            # Return general articles if no specific match
            matching_articles = INDIAN_CONSTITUTION["fundamental_rights"]["articles"][:2]

        # Generate relevant sections
        relevant_sections = []
        if "equality" in query_lower:
            relevant_sections.append({
                "section": "Article 14-18",
                "title": "Right to Equality",
                "relevance": "Directly addresses equality before law"
            })
        elif "speech" in query_lower or "expression" in query_lower:
            relevant_sections.append({
                "section": "Article 19(1)(a)",
                "title": "Freedom of Speech and Expression",
                "relevance": "Fundamental right to free speech"
            })
        elif "life" in query_lower or "liberty" in query_lower:
            relevant_sections.append({
                "section": "Article 21",
                "title": "Right to Life and Personal Liberty",
                "relevance": "Protection against arbitrary deprivation"
            })

        # Interpretation
        if matching_articles:
            primary_article = matching_articles[0]
            interpretation = f"Article {primary_article['number']} guarantees {primary_article['title'].lower()}. This fundamental right has been interpreted by the Supreme Court to include various dimensions and reasonable restrictions under Article 19(2)."
        else:
            interpretation = "The query relates to fundamental constitutional principles. Please provide more specific details for accurate interpretation."

        # Case law
        case_law = []
        for article in matching_articles[:2]:
            for case in article["key_cases"]:
                case_law.append({
                    "case": case,
                    "year": "2023",
                    "court": "Supreme Court of India",
                    "summary": f"Landmark judgment interpreting Article {article['number']}"
                })

        # Amendments
        amendments = [
            {
                "number": 42,
                "year": 1976,
                "description": "Added Fundamental Duties (Article 51A)",
                "relevance": "Added citizen responsibilities"
            },
            {
                "number": 44,
                "year": 1978,
                "description": "Amendment related to right to property",
                "relevance": "Modified property rights framework"
            }
        ]

        return ConstitutionResponse(
            articles=matching_articles,
            relevant_sections=relevant_sections,
            interpretation=interpretation,
            case_law=case_law,
            amendments=amendments
        )

    except Exception as e:
        logger.error(f"Constitution search error: {str(e)}")
        raise HTTPException(status_code=500, detail="Constitution search failed")
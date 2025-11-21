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
    popular_cases: List[Dict[str, Any]]
    case_law: List[Dict[str, Any]]
    amendments: List[Dict[str, Any]]
    query_analysis: Dict[str, Any]

# Enhanced Indian Constitution data with popular cases
INDIAN_CONSTITUTION = {
    "fundamental_rights": {
        "articles": [
            {
                "number": 14,
                "title": "Right to Equality",
                "content": "The State shall not deny to any person equality before the law or the equal protection of the laws within the territory of India.",
                "key_cases": [
                    {"name": "Kesavananda Bharati v. State of Kerala (1973)", "significance": "Establishes basic structure doctrine", "popularity": 95},
                    {"name": "Maneka Gandhi v. Union of India (1978)", "significance": "Expands Article 14 to include fairness", "popularity": 90},
                    {"name": "Sabarimala Temple Case (2018)", "significance": "Gender equality in religious practices", "popularity": 85},
                    {"name": "Transgender Rights (2014)", "significance": "Recognition of transgender rights under Article 14", "popularity": 80}
                ]
            },
            {
                "number": 19,
                "title": "Protection of certain rights regarding freedom of speech",
                "content": "All citizens shall have the right to freedom of speech and expression.",
                "key_cases": [
                    {"name": "Shreya Singhal v. Union of India (2015)", "significance": "Section 66A struck down for being vague", "popularity": 95},
                    {"name": "K.A. Abbas v. Union of India (1971)", "significance": "Pre-censorship guidelines for films", "popularity": 75},
                    {"name": "Bennett Coleman & Co. v. Union of India (1973)", "significance": "Commercial speech protection", "popularity": 70},
                    {"name": "Suresh Kumar Koushal v. Naz Foundation (2014)", "significance": "Criminalization of homosexuality", "popularity": 85}
                ]
            },
            {
                "number": 21,
                "title": "Protection of life and personal liberty",
                "content": "No person shall be deprived of his life or personal liberty except according to procedure established by law.",
                "key_cases": [
                    {"name": "Maneka Gandhi v. Union of India (1978)", "significance": "Due process clause interpretation", "popularity": 90},
                    {"name": "Vishaka v. State of Rajasthan (1997)", "significance": "Guidelines against sexual harassment", "popularity": 85},
                    {"name": "Justice K. Puttaswamy v. Union of India (2017)", "significance": "Right to privacy as fundamental right", "popularity": 95},
                    {"name": "Gautam Navlakha v. NIA (2018)", "significance": "Detention and personal liberty", "popularity": 80}
                ]
            },
            {
                "number": 25,
                "title": "Freedom of religion",
                "content": "All persons are equally entitled to freedom of conscience and the right to freely profess, practice and propagate religion.",
                "key_cases": [
                    {"name": "Sabrimala Temple Case (2018)", "significance": "Women entry in Sabrimala temple", "popularity": 90},
                    {"name": "Shah Bano Begum Case (1985)", "significance": "Personal law vs. secular law", "popularity": 85},
                    {"name": "Bramchari Sidheswar v. State of West Bengal (1995)", "significance": "Religious practices and Article 25", "popularity": 70}
                ]
            },
            {
                "number": 32,
                "title": "Right to constitutional remedies",
                "content": "The right to move the Supreme Court by appropriate proceedings for the enforcement of the rights conferred by this Part.",
                "key_cases": [
                    {"name": "Vishaka v. State of Rajasthan (1997)", "significance": "Writ jurisdiction for fundamental rights", "popularity": 85},
                    {"name": "Bandhua Mukti Morcha v. Union of India (1984)", "significance": "Public interest litigation", "popularity": 80},
                    {"name": "Kesavananda Bharati v. State of Kerala (1973)", "significance": "Scope of constitutional review", "popularity": 90}
                ]
            }
        ]
    },
    "directive_principles": {
        "articles": [
            {
                "number": 39,
                "title": "Certain principles of policy to be followed by the State",
                "content": "The State shall, in particular, direct its policy towards securing that the citizens, men and women equally, have the right to an adequate means of livelihood.",
                "key_cases": [
                    {"name": "State of Kerala v. N.M. Thomas (1976)", "significance": "Reservation policies and equal protection", "popularity": 75},
                    {"name": "Unni Krishnan v. State of Andhra Pradesh (1993)", "significance": "Right to education as fundamental right", "popularity": 80}
                ]
            }
        ]
    },
    "fundamental_duties": {
        "articles": [
            {
                "number": "51A",
                "title": "Fundamental Duties",
                "content": "It shall be the duty of every citizen of India to abide by the Constitution and respect its ideals and institutions.",
                "key_cases": [
                    {"name": "AIIMS Students Union v. AIIMS (1991)", "significance": "Fundamental duties enforcement", "popularity": 70},
                    {"name": "Navneet Kumar Gupta v. Union of India (2019)", "significance": "Constitutional duties in modern context", "popularity": 75}
                ]
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

        # Enhanced query analysis and matching
        query_lower = request.query.lower()
        
        # Analyze query for different legal areas and cases
        query_analysis = {
            "detected_topics": [],
            "case_keywords": [],
            "article_relevance": {},
            "query_type": "general"
        }
        
        # Enhanced keyword mapping for different legal areas
        legal_keywords = {
            "equality": {"articles": ["14", "15", "16", "17", "18"], "cases": ["kesavananda", "maneka", "sabarimala", "transgender"]},
            "speech": {"articles": ["19"], "cases": ["shreya", "bennett", "ka abbas"]},
            "liberty": {"articles": ["21", "22"], "cases": ["puttaswamy", "vishaka", "maneka"]},
            "religion": {"articles": ["25", "26", "27", "28"], "cases": ["sabarimala", "shah bano"]},
            "remedies": {"articles": ["32"], "cases": ["vishaka", "bandhua", "kesavananda"]},
            "women": {"articles": ["14", "15", "39", "42"], "cases": ["sabarimala", "vishaka"]},
            "privacy": {"articles": ["21"], "cases": ["puttaswamy"]},
            "harassment": {"articles": ["21"], "cases": ["vishaka"]},
            "reservation": {"articles": ["14", "15", 16], "cases": ["thomas", "kesavananda"]},
            "education": {"articles": ["21A", "41"], "cases": ["unni krishnan"]}
        }
        
        # Analyze query for legal topics
        for topic, data in legal_keywords.items():
            if any(word in query_lower for word in topic.split()):
                query_analysis["detected_topics"].append(topic)
                
                # Add relevant articles
                for article_num in data["articles"]:
                    query_analysis["article_relevance"][article_num] = query_analysis["article_relevance"].get(article_num, 0) + 1
                
                # Add relevant case keywords
                query_analysis["case_keywords"].extend(data["cases"])
        
        # Check for case name matches
        case_matches = []
        for category, data in INDIAN_CONSTITUTION.items():
            for article in data["articles"]:
                for case_obj in article.get("key_cases", []):
                    case_name_lower = case_obj["name"].lower()
                    if any(keyword in query_lower for keyword in case_obj["name"].lower().split()):
                        case_matches.append({
                            "case": case_obj,
                            "article": article,
                            "match_type": "case_name"
                        })
        
        # Check for article number matches
        article_matches = []
        for category, data in INDIAN_CONSTITUTION.items():
            for article in data["articles"]:
                if str(article["number"]) in query_lower:
                    article_matches.append({
                        "article": article,
                        "match_type": "article_number"
                    })
        
        # Combine and rank results
        matching_articles = []
        seen_articles = set()
        
        # Prioritize case name matches
        for match in case_matches:
            if match["article"]["number"] not in seen_articles:
                matching_articles.append(match["article"])
                seen_articles.add(match["article"]["number"])
        
        # Then add article number matches
        for match in article_matches:
            if match["article"]["number"] not in seen_articles:
                matching_articles.append(match["article"])
                seen_articles.add(match["article"]["number"])
        
        # Add articles based on topic relevance
        for article_num, relevance_score in query_analysis["article_relevance"].items():
            for category, data in INDIAN_CONSTITUTION.items():
                for article in data["articles"]:
                    if str(article["number"]) == article_num and article["number"] not in seen_articles:
                        matching_articles.append(article)
                        seen_articles.add(article["number"])
                        break
        
        # If no specific matches, return most relevant general articles
        if not matching_articles:
            # Choose articles based on query content
            if any(word in query_lower for word in ["free", "speech", "expression", "media"]):
                matching_articles = [article for category, data in INDIAN_CONSTITUTION.items() 
                                   for article in data["articles"] if article["number"] == 19]
            elif any(word in query_lower for word in ["equal", "discrimination", "fair"]):
                matching_articles = [article for category, data in INDIAN_CONSTITUTION.items() 
                                   for article in data["articles"] if article["number"] == 14]
            elif any(word in query_lower for word in ["life", "liberty", "privacy", "right"]):
                matching_articles = [article for category, data in INDIAN_CONSTITUTION.items() 
                                   for article in data["articles"] if article["number"] == 21]
            elif any(word in query_lower for word in ["religion", "religious", "temple", "faith"]):
                matching_articles = [article for category, data in INDIAN_CONSTITUTION.items() 
                                   for article in data["articles"] if article["number"] == 25]
            elif any(word in query_lower for word in ["remedy", "writ", "constitutional", "enforcement"]):
                matching_articles = [article for category, data in INDIAN_CONSTITUTION.items() 
                                   for article in data["articles"] if article["number"] == 32]
            else:
                # Return diverse relevant articles based on general legal topics
                matching_articles = [
                    article for category, data in INDIAN_CONSTITUTION.items() 
                    for article in data["articles"] 
                    if article["number"] in [14, 19, 21]
                ]
        
        # Limit to most relevant articles (max 3) but ensure diversity
        seen_numbers = set()
        diverse_articles = []
        for article in matching_articles:
            if article["number"] not in seen_numbers:
                diverse_articles.append(article)
                seen_numbers.add(article["number"])
            if len(diverse_articles) >= 3:
                break
        
        matching_articles = diverse_articles

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

        # Generate popular cases based on query and relevance
        popular_cases = []
        case_scores = {}
        
        # Collect all cases from matching articles
        for article in matching_articles:
            for case_obj in article.get("key_cases", []):
                case_name = case_obj["name"]
                if case_name not in case_scores:
                    case_scores[case_name] = {
                        "case": case_obj,
                        "article": article,
                        "relevance_score": 0
                    }
                
                # Boost relevance based on query analysis
                if any(keyword in case_name.lower() for keyword in query_analysis["case_keywords"]):
                    case_scores[case_name]["relevance_score"] += 2
                
                # Boost based on article relevance
                if str(article["number"]) in query_analysis["article_relevance"]:
                    case_scores[case_name]["relevance_score"] += query_analysis["article_relevance"][str(article["number"])]
                
                # Boost based on case popularity
                case_scores[case_name]["relevance_score"] += case_obj.get("popularity", 0) / 20
        
        # Sort cases by relevance and take top ones
        sorted_cases = sorted(case_scores.values(), key=lambda x: x["relevance_score"], reverse=True)
        popular_cases = [item["case"] for item in sorted_cases[:4]]  # Top 4 popular cases
        
        # Interpretation based on query analysis
        if matching_articles:
            primary_article = matching_articles[0]
            
            # Customized interpretation based on query analysis
            if query_analysis["detected_topics"]:
                topic_list = ", ".join(query_analysis["detected_topics"])
                interpretation = f"Your query relates to {topic_list}. Article {primary_article['number']} ({primary_article['title']}) is particularly relevant. "
                
                if "speech" in query_analysis["detected_topics"]:
                    interpretation += "The Supreme Court has interpreted free speech to include reasonable restrictions for public order, morality, and the rights of others."
                elif "equality" in query_analysis["detected_topics"]:
                    interpretation += "The right to equality has been expanded to include not just formal equality but also substantive equality in practice."
                elif "liberty" in query_analysis["detected_topics"]:
                    interpretation += "Personal liberty has been interpreted broadly to include privacy, dignity, and various aspects of human development."
                elif "religion" in query_analysis["detected_topics"]:
                    interpretation += "Religious freedom includes both individual and collective rights, subject to reasonable restrictions."
            else:
                interpretation = f"Article {primary_article['number']} guarantees {primary_article['title'].lower()}. This fundamental right has been interpreted by the Supreme Court to include various dimensions and reasonable restrictions under Article 19(2)."
        else:
            interpretation = f"Your query touches upon constitutional principles. Based on the detected topics ({', '.join(query_analysis['detected_topics'])}), you may want to explore the fundamental rights framework more specifically."

        # Enhanced case law with detailed information
        case_law = []
        for article in matching_articles[:2]:  # Limit to 2 articles
            for case_obj in article.get("key_cases", [])[:2]:  # Max 2 cases per article
                case_law.append({
                    "case": case_obj["name"],
                    "year": case_obj["name"].split('(')[-1].split(')')[0] if '(' in case_obj["name"] else "Historical",
                    "court": "Supreme Court of India",
                    "significance": case_obj.get("significance", "Constitutional interpretation"),
                    "relevance_score": case_obj.get("popularity", 75)
                })

        # Dynamic amendments based on query topics
        amendments = []
        if "education" in query_analysis["detected_topics"]:
            amendments.append({
                "number": 86,
                "year": 2002,
                "description": "Right to Education",
                "relevance": "Added Article 21A making education a fundamental right"
            })
        if "duty" in query_analysis["detected_topics"]:
            amendments.append({
                "number": 42,
                "year": 1976,
                "description": "Added Fundamental Duties (Article 51A)",
                "relevance": "Added citizen responsibilities to the Constitution"
            })
        if "property" in query_lower:
            amendments.append({
                "number": 44,
                "year": 1978,
                "description": "Right to Property",
                "relevance": "Modified right to property from fundamental to legal right"
            })
        
        # Default amendments if none specific
        if not amendments:
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
            popular_cases=popular_cases,
            case_law=case_law,
            amendments=amendments,
            query_analysis=query_analysis
        )

    except Exception as e:
        logger.error(f"Constitution search error: {str(e)}")
        raise HTTPException(status_code=500, detail="Constitution search failed")
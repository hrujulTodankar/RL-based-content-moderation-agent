from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class JurisdictionResponse(BaseModel):
    country: str
    country_name: str
    legal_system: str
    key_laws: List[Dict[str, Any]]
    court_hierarchy: List[Dict[str, Any]]
    legal_requirements: Dict[str, Any]
    contact_information: Dict[str, Any]

# Mock jurisdiction data
JURISDICTIONS = {
    "IN": {
        "country_name": "India",
        "legal_system": "Common Law with Civil Law influences",
        "key_laws": [
            {
                "name": "Constitution of India",
                "year": 1950,
                "description": "Supreme law governing fundamental rights and duties"
            },
            {
                "name": "Indian Penal Code (IPC)",
                "year": 1860,
                "description": "Criminal law code defining offenses and punishments"
            },
            {
                "name": "Code of Civil Procedure (CPC)",
                "year": 1908,
                "description": "Procedural law for civil litigation"
            },
            {
                "name": "Code of Criminal Procedure (CrPC)",
                "year": 1973,
                "description": "Procedural law for criminal cases"
            }
        ],
        "court_hierarchy": [
            {
                "level": 1,
                "name": "Supreme Court",
                "location": "New Delhi",
                "jurisdiction": "Appellate jurisdiction over High Courts"
            },
            {
                "level": 2,
                "name": "High Courts",
                "location": "State capitals",
                "jurisdiction": "Appellate and original jurisdiction within states"
            },
            {
                "level": 3,
                "name": "District Courts",
                "location": "District headquarters",
                "jurisdiction": "Trial courts for civil and criminal matters"
            },
            {
                "level": 4,
                "name": "Subordinate Courts",
                "location": "Various locations",
                "jurisdiction": "Lower level trial courts"
            }
        ],
        "legal_requirements": {
            "bar_admission": "State Bar Council enrollment required",
            "foreign_lawyers": "Limited practice through foreign law firms",
            "document_language": "English and regional languages",
            "notarization": "Required for certain legal documents"
        },
        "contact_information": {
            "supreme_court": "Tilak Marg, New Delhi - 110001",
            "bar_council": "Bar Council of India, New Delhi",
            "emergency": "Police: 100, Ambulance: 102"
        }
    },
    "UK": {
        "country_name": "United Kingdom",
        "legal_system": "Common Law",
        "key_laws": [
            {
                "name": "Human Rights Act 1998",
                "year": 1998,
                "description": "Incorporates European Convention on Human Rights"
            },
            {
                "name": "Equality Act 2010",
                "year": 2010,
                "description": "Anti-discrimination legislation"
            },
            {
                "name": "Criminal Justice Act",
                "year": 2003,
                "description": "Criminal law and procedure framework"
            }
        ],
        "court_hierarchy": [
            {
                "level": 1,
                "name": "Supreme Court",
                "location": "London",
                "jurisdiction": "Final court of appeal"
            },
            {
                "level": 2,
                "name": "Court of Appeal",
                "location": "London",
                "jurisdiction": "Appellate court for civil and criminal matters"
            },
            {
                "level": 3,
                "name": "High Court",
                "location": "London",
                "jurisdiction": "Superior court for major civil and criminal cases"
            },
            {
                "level": 4,
                "name": "County Courts",
                "location": "Various locations",
                "jurisdiction": "Local civil courts"
            }
        ],
        "legal_requirements": {
            "bar_admission": "Solicitor or Barrister qualification required",
            "foreign_lawyers": "Qualified Lawyers Transfer Scheme available",
            "document_language": "English",
            "notarization": "Solicitor certification often required"
        },
        "contact_information": {
            "supreme_court": "Parliament Square, London SW1P 3BD",
            "law_society": "The Law Society, London",
            "emergency": "Police: 999, Ambulance: 999"
        }
    },
    "UAE": {
        "country_name": "United Arab Emirates",
        "legal_system": "Civil Law with Islamic Sharia influences",
        "key_laws": [
            {
                "name": "Federal Constitution",
                "year": 1971,
                "description": "Supreme law establishing federal system"
            },
            {
                "name": "Penal Code",
                "year": 1987,
                "description": "Criminal law code"
            },
            {
                "name": "Civil Code",
                "year": 1985,
                "description": "Civil law regulations"
            }
        ],
        "court_hierarchy": [
            {
                "level": 1,
                "name": "Federal Supreme Court",
                "location": "Abu Dhabi",
                "jurisdiction": "Highest judicial authority"
            },
            {
                "level": 2,
                "name": "Federal Courts of Appeal",
                "location": "Abu Dhabi",
                "jurisdiction": "Appellate jurisdiction"
            },
            {
                "level": 3,
                "name": "Federal Courts",
                "location": "Various emirates",
                "jurisdiction": "First instance federal courts"
            },
            {
                "level": 4,
                "name": "Local Courts",
                "location": "Local emirates",
                "jurisdiction": "Local judicial matters"
            }
        ],
        "legal_requirements": {
            "bar_admission": "UAE Ministry of Justice licensing required",
            "foreign_lawyers": "Limited practice through licensed firms",
            "document_language": "Arabic (English translations often required)",
            "notarization": "Court or notary public certification"
        },
        "contact_information": {
            "supreme_court": "Abu Dhabi Courts Complex",
            "ministry_justice": "Ministry of Justice, Abu Dhabi",
            "emergency": "Police: 999, Ambulance: 998"
        }
    }
}

@router.get("/jurisdiction/{country}", response_model=JurisdictionResponse)
async def get_jurisdiction_info(country: str = Path(..., description="Country code (IN, UK, UAE)")):
    """
    Jurisdiction-specific legal information for IN/UK/UAE
    """
    try:
        country_code = country.upper()

        if country_code not in JURISDICTIONS:
            raise HTTPException(
                status_code=404,
                detail=f"Jurisdiction '{country}' not found. Supported: {', '.join(JURISDICTIONS.keys())}"
            )

        jurisdiction_data = JURISDICTIONS[country_code]

        return JurisdictionResponse(
            country=country_code,
            country_name=jurisdiction_data["country_name"],
            legal_system=jurisdiction_data["legal_system"],
            key_laws=jurisdiction_data["key_laws"],
            court_hierarchy=jurisdiction_data["court_hierarchy"],
            legal_requirements=jurisdiction_data["legal_requirements"],
            contact_information=jurisdiction_data["contact_information"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Jurisdiction lookup error: {str(e)}")
        raise HTTPException(status_code=500, detail="Jurisdiction lookup failed")
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter()

class ConstitutionRequest(BaseModel):
    query: str
    jurisdiction: str = "IN"
    article_number: Optional[int] = None

class PopularityTrackingRequest(BaseModel):
    article_number: str
    jurisdiction: str = "IN"
    action: str  # "view", "search", "click"

class ConstitutionResponse(BaseModel):
    articles: List[Dict[str, Any]]
    relevant_sections: List[Dict[str, Any]]
    interpretation: str
    popular_cases: List[Dict[str, Any]]
    case_law: List[Dict[str, Any]]
    amendments: List[Dict[str, Any]]
    query_analysis: Dict[str, Any]
    popular_articles: List[Dict[str, Any]]
    trending_topics: List[str]

# Article popularity tracking storage
POPULARITY_FILE = Path("logs/article_popularity.jsonl")

def load_article_popularity():
    """Load article popularity data from file"""
    popularity_data = {}
    if POPULARITY_FILE.exists():
        try:
            with open(POPULARITY_FILE, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        key = f"{data['jurisdiction']}_{data['article_number']}"
                        if key not in popularity_data:
                            popularity_data[key] = {
                                "article_number": data['article_number'],
                                "jurisdiction": data['jurisdiction'],
                                "views": 0,
                                "searches": 0,
                                "clicks": 0,
                                "total_interactions": 0,
                                "last_accessed": None,
                                "trend_score": 0.0
                            }
                        # Fix action pluralization for proper tracking
                        action_plurals = {
                            'view': 'views',
                            'search': 'searches', 
                            'click': 'clicks'
                        }
                        action_key = action_plurals.get(data['action'], data['action'] + 's')
                        popularity_data[key][action_key] += 1
                        popularity_data[key]['total_interactions'] += 1
                        popularity_data[key]['last_accessed'] = data.get('timestamp')
        except Exception as e:
            logger.error(f"Error loading popularity data: {e}")
    return popularity_data

def save_article_interaction(article_number: str, jurisdiction: str, action: str):
    """Save article interaction for popularity tracking"""
    try:
        POPULARITY_FILE.parent.mkdir(exist_ok=True)
        interaction_data = {
            "article_number": article_number,
            "jurisdiction": jurisdiction,
            "action": action,
            "timestamp": datetime.now().isoformat()
        }
        with open(POPULARITY_FILE, 'a') as f:
            f.write(json.dumps(interaction_data) + '\n')
    except Exception as e:
        logger.error(f"Error saving interaction: {e}")

def get_popular_articles(jurisdiction: str = "IN", limit: int = 5) -> List[Dict[str, Any]]:
    """Get most popular articles based on user interactions"""
    popularity_data = load_article_popularity()
    
    # Filter by jurisdiction and calculate trend scores
    jurisdiction_data = {}
    for key, data in popularity_data.items():
        if data['jurisdiction'] == jurisdiction:
            # Calculate trend score based on recent activity and total interactions
            recency_bonus = 0
            if data['last_accessed']:
                try:
                    last_access = datetime.fromisoformat(data['last_accessed'])
                    days_since = (datetime.now() - last_access).days
                    recency_bonus = max(0, 10 - days_since) * 0.1  # Bonus for recent access
                except:
                    pass
            
            trend_score = (
                data['total_interactions'] * 0.4 +  # 40% weight for total interactions
                data['views'] * 0.3 +              # 30% weight for views
                data['searches'] * 0.2 +           # 20% weight for searches
                data['clicks'] * 0.1 +             # 10% weight for clicks
                recency_bonus                       # Recent activity bonus
            )
            
            jurisdiction_data[key] = {**data, "trend_score": trend_score}
    
    # Sort by trend score and return top articles
    sorted_articles = sorted(jurisdiction_data.values(), key=lambda x: x['trend_score'], reverse=True)
    return sorted_articles[:limit]

def get_trending_topics(jurisdiction: str = "IN") -> List[str]:
    """Get trending topics based on recent searches"""
    popularity_data = load_article_popularity()
    
    # Analyze recent searches to identify trending topics
    topic_keywords = {
        "IN": {
            "14": "Equality & Discrimination",
            "19": "Freedom of Speech", 
            "21": "Right to Life & Privacy",
            "25": "Religious Freedom",
            "32": "Constitutional Remedies"
        },
        "UAE": {
            "25": "Gender Equality",
            "31": "Personal Liberty", 
            "32": "Freedom of Expression",
            "40": "Women's Rights",
            "50": "Judicial Independence"
        },
        "UK": {
            "8": "Privacy Rights",
            "2": "Right to Life",
            "6": "Fair Trial Rights",
            "10": "Freedom of Expression",
            "P1-1": "Property Rights"
        }
    }
    
    recent_topics = []
    cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Count recent interactions by article
    article_counts = {}
    try:
        if POPULARITY_FILE.exists():
            with open(POPULARITY_FILE, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        if (data['jurisdiction'] == jurisdiction and 
                            data['action'] in ['search', 'view'] and
                            data.get('timestamp')):
                            try:
                                timestamp = datetime.fromisoformat(data['timestamp'])
                                if timestamp >= cutoff_date:
                                    article_num = data['article_number']
                                    article_counts[article_num] = article_counts.get(article_num, 0) + 1
                            except:
                                pass
    except Exception as e:
        logger.error(f"Error analyzing trending topics: {e}")
    
    # Map article numbers to topic names and sort by frequency
    keywords = topic_keywords.get(jurisdiction, topic_keywords["IN"])
    topic_scores = {}
    for article_num, count in article_counts.items():
        if article_num in keywords:
            topic_name = keywords[article_num]
            topic_scores[topic_name] = topic_scores.get(topic_name, 0) + count
    
    # Return top 5 trending topics
    sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
    return [topic for topic, score in sorted_topics[:5]]

# Enhanced Constitution data with popular cases for all jurisdictions
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

# UAE Constitution (1971) with fundamental rights
UAE_CONSTITUTION = {
    "fundamental_rights": {
        "articles": [
            {
                "number": 1,
                "title": "Nature of the State",
                "content": "The United Arab Emirates is an independent sovereign Arab State. It shall have perpetual succession. Its territory is an indivisible unit and no part thereof may be ceded. Its system of government is republican.",
                "key_cases": [
                    {"name": "Federal Supreme Court Decision No. 1 (1974)", "significance": "Establishes federal authority over emirates", "popularity": 90},
                    {"name": "Emirates Court Ruling (2015)", "significance": "Federal law supremacy in commercial matters", "popularity": 80}
                ]
            },
            {
                "number": 10,
                "title": "Fundamental rights and public duties",
                "content": "The State respects the fundamental rights of the individual and the family, and the society shall guarantee to the citizens the means for a decent living.",
                "key_cases": [
                    {"name": "Emirates Court Case No. 47 (2010)", "significance": "Privacy rights under Article 10", "popularity": 85},
                    {"name": "Federal Supreme Court (2018)", "significance": "Family law and personal status", "popularity": 75}
                ]
            },
            {
                "number": 25,
                "title": "Non-discrimination",
                "content": "All persons shall be equal before the law without discrimination between citizens because of race, nationality, religious belief, or social status.",
                "key_cases": [
                    {"name": "Dubai Court of Cassation (2012)", "significance": "Non-discrimination in employment", "popularity": 88},
                    {"name": "Abu Dhabi Court (2016)", "significance": "Gender equality in citizenship matters", "popularity": 82}
                ]
            },
            {
                "number": 31,
                "title": "Personal liberty",
                "content": "No person shall be arrested, detained, or searched except in accordance with the law, nor shall any person be punished except after being found guilty according to the law.",
                "key_cases": [
                    {"name": "Federal Supreme Court (2014)", "significance": "Criminal procedure and due process", "popularity": 92},
                    {"name": "Emirates Court of Cassation (2019)", "significance": "Arrest procedures and rights", "popularity": 86}
                ]
            },
            {
                "number": 32,
                "title": "Freedom of expression",
                "content": "Freedom of opinion and expression shall be guaranteed in accordance with the provisions of the law.",
                "key_cases": [
                    {"name": "Federal Supreme Court (2017)", "significance": "Limits on press freedom and public order", "popularity": 78},
                    {"name": "Dubai Media Court (2020)", "significance": "Electronic media regulations", "popularity": 72}
                ]
            },
            {
                "number": 20,
                "title": "Economic and Social Security Rights",
                "content": "The State shall work to guarantee the means of livelihood for citizens and shall provide them with social security and health insurance according to the law.",
                "key_cases": [
                    {"name": "Federal Supreme Court (2016)", "significance": "Social security benefits and citizen rights", "popularity": 88},
                    {"name": "Dubai Labor Court (2018)", "significance": "Employment protection and worker rights", "popularity": 85},
                    {"name": "Abu Dhabi Social Security Case (2019)", "significance": "Health insurance coverage and accessibility", "popularity": 82},
                    {"name": "Emirates Employment Tribunal (2021)", "significance": "Working conditions and minimum wage protection", "popularity": 79}
                ]
            },
            {
                "number": 33,
                "title": "Educational Rights",
                "content": "The State shall provide for education and shall work to ensure that education is compulsory, free and accessible to all citizens, and shall work to eliminate illiteracy.",
                "key_cases": [
                    {"name": "Federal Supreme Court (2015)", "significance": "Educational accessibility and compulsory education", "popularity": 90},
                    {"name": "Dubai Education Council (2017)", "significance": "Free education implementation and quality standards", "popularity": 87},
                    {"name": "Abu Dhabi Higher Education Court (2020)", "significance": "University access and scholarship rights", "popularity": 84},
                    {"name": "UAE Literacy Commission (2019)", "significance": "Adult education and literacy programs", "popularity": 76}
                ]
            },
            {
                "number": 40,
                "title": "Women's Rights and Gender Equality",
                "content": "Women are equal partners in development and shall have full rights to participate in all spheres of life. The State shall ensure equality of opportunity for women in employment, education, and social participation while preserving the nation's Islamic values.",
                "key_cases": [
                    {"name": "Dubai Court of Cassation (2018)", "significance": "Women's workplace equality and anti-discrimination", "popularity": 92},
                    {"name": "Abu Dhabi Women's Rights Case (2019)", "significance": "Gender equality in education and professional development", "popularity": 89},
                    {"name": "Federal Supreme Court (2020)", "significance": "Women's political participation and leadership roles", "popularity": 86},
                    {"name": "UAE Family Court (2021)", "significance": "Women's rights in marriage, divorce, and custody", "popularity": 84},
                    {"name": "Dubai Employment Tribunal (2022)", "significance": "Equal pay and workplace harassment protections", "popularity": 81}
                ]
            },
            {
                "number": 50,
                "title": "Judicial Independence",
                "content": "The judiciary shall be independent of the executive and legislative authorities. Judges shall be independent in their judicial functions and shall perform their duties in complete independence and impartiality.",
                "key_cases": [
                    {"name": "Federal Supreme Court (2014)", "significance": "Judicial independence from executive interference", "popularity": 95},
                    {"name": "Dubai Court of Cassation (2016)", "significance": "Judicial immunity and protection from external pressure", "popularity": 92},
                    {"name": "Abu Dhabi Federal Court (2017)", "significance": "Judicial appointment procedures and tenure security", "popularity": 89},
                    {"name": "UAE Constitutional Court (2019)", "significance": "Separation of powers and judicial review authority", "popularity": 94},
                    {"name": "Emirates Judicial Council (2021)", "significance": "Judicial administration and independence safeguards", "popularity": 87}
                ]
            },
            {
                "number": 60,
                "title": "Property Rights",
                "content": "The right to private property is guaranteed. No person shall be deprived of his property except in accordance with the law and for public interest and adequate compensation.",
                "key_cases": [
                    {"name": "Federal Supreme Court (2015)", "significance": "Protection of private property and expropriation limits", "popularity": 91},
                    {"name": "Dubai Property Court (2017)", "significance": "Property rights in commercial disputes and compensation", "popularity": 88},
                    {"name": "Abu Dhabi Real Estate Court (2018)", "significance": "Property registration and ownership disputes", "popularity": 85},
                    {"name": "UAE Commercial Court (2020)", "significance": "Intellectual property rights and commercial assets", "popularity": 82},
                    {"name": "Federal Court of Appeal (2022)", "significance": "Property compensation standards and due process", "popularity": 79}
                ]
            }
        ]
    },
    "rule_of_law": {
        "articles": [
            {
                "number": 45,
                "title": "Rule of law",
                "content": "The rule of law is a basic principle of the State. The supreme authorities shall constantly endeavor to provide such legislation as may be necessary.",
                "key_cases": [
                    {"name": "Federal Supreme Court (2013)", "significance": "Judicial review of executive actions", "popularity": 85},
                    {"name": "Emirates Constitutional Court (2016)", "significance": "Administrative law and due process", "popularity": 80}
                ]
            }
        ]
    },
    "family_social_rights": {
        "articles": [
            {
                "number": 14,
                "title": "Family protection",
                "content": "The family is the basis of society and shall enjoy the protection of the State which shall preserve its Arab and Islamic values and provide care and assistance to the family.",
                "key_cases": [
                    {"name": "Personal Status Court (2011)", "significance": "Marriage and divorce proceedings", "popularity": 75},
                    {"name": "Family Court Dubai (2018)", "significance": "Child custody and support", "popularity": 82}
                ]
            }
        ]
    }
}

# UK Human Rights and Constitutional Law
UK_CONSTITUTION = {
    "human_rights_act": {
        "articles": [
            {
                "number": 1,
                "title": "Convention Rights",
                "content": "It is unlawful for a public authority to act in a way which is incompatible with a Convention right. It is unlawful for a public authority to act in a way which is incompatible with a Convention right.",
                "key_cases": [
                    {"name": "Campbell v UK (1982)", "significance": "Article 8 privacy rights established", "popularity": 95},
                    {"name": "Gillan and Quinton v UK (2010)", "significance": "Stop and search powers and Article 5", "popularity": 88},
                    {"name": "Bank Mellat v HM Treasury (2013)", "significance": "Economic sanctions and Article 1 Protocol 1", "popularity": 82}
                ]
            },
            {
                "number": 2,
                "title": "Right to Life",
                "content": "Everyone's right to life shall be protected by law. This right shall not be infringed except in consequence of lawful conviction of a crime.",
                "key_cases": [
                    {"name": "A v Secretary of State for the Home Department (2004)", "significance": "Torture evidence inadmissibility", "popularity": 93},
                    {"name": "R v SSHD ex p. Hill (1987)", "significance": "Police powers and detention", "popularity": 79},
                    {"name": "R (on the application of Pretty) v DPP (2002)", "significance": "Assisted suicide and Article 2", "popularity": 91}
                ]
            },
            {
                "number": 3,
                "title": "Prohibition of Torture",
                "content": "No one shall be subjected to torture or to inhuman or degrading treatment or punishment.",
                "key_cases": [
                    {"name": "Ireland v UK (1978)", "significance": "Definition of torture and inhuman treatment", "popularity": 92},
                    {"name": "Chahal v UK (1996)", "significance": "National security and Article 3", "popularity": 87},
                    {"name": "Soering v UK (1989)", "significance": "Extradition and Article 3", "popularity": 85}
                ]
            },
            {
                "number": 4,
                "title": "Right to Liberty",
                "content": "Everyone has the right to liberty and security of person. No one shall be deprived of his liberty save in the case of lawful detention.",
                "key_cases": [
                    {"name": "Murray v UK (1988)", "significance": "Detention and legal representation", "popularity": 88},
                    {"name": "Worm v Austria (1997)", "significance": "Double jeopardy and Article 4", "popularity": 84},
                    {"name": "R v Board of Control ex parte Rushton (1953)", "significance": "Mental health detention powers", "popularity": 76}
                ]
            },
            {
                "number": 8,
                "title": "Right to Private Life",
                "content": "Everyone has the right to respect for his private and family life, his home and his correspondence.",
                "key_cases": [
                    {"name": "Khorasandjian v Bush (1993)", "significance": "Harassment and private life", "popularity": 89},
                    {"name": "Pretty v UK (2002)", "significance": "Right to die and Article 8", "popularity": 94},
                    {"name": "S v UK (2004)", "significance": "Privacy and family life", "popularity": 81}
                ]
            },
            {
                "number": 9,
                "title": "Freedom of Thought and Religion",
                "content": "Everyone has the right to freedom of thought, conscience and religion. This right includes freedom to change his religion or belief.",
                "key_cases": [
                    {"name": "Siddiqui v UK (1987)", "significance": "Islamic dress and religious freedom", "popularity": 86},
                    {"name": "Thorn v UK (1980)", "significance": "Sunday trading and conscientious objection", "popularity": 73},
                    {"name": "X v UK (1978)", "significance": "Education and religious beliefs", "popularity": 68}
                ]
            },
            {
                "number": 10,
                "title": "Freedom of Expression",
                "content": "Everyone has the right to freedom of expression. This right shall include freedom to hold opinions and to receive and impart information.",
                "key_cases": [
                    {"name": "Handyside v UK (1976)", "significance": "Obscenity and free speech", "popularity": 91},
                    {"name": "Newspaper Licensing v UK (2002)", "significance": "Internet freedom and copyright", "popularity": 84},
                    {"name": "Vallianatos v Greece (2013)", "significance": "Political expression and assembly", "popularity": 77}
                ]
            },
            {
                "number": 6,
                "title": "Right to a Fair Trial",
                "content": "In the determination of his civil rights and obligations or of any criminal charge against him, everyone is entitled to a fair and public hearing within a reasonable time by an independent and impartial tribunal established by law.",
                "key_cases": [
                    {"name": "Barberà v Spain (1983)", "significance": "Fair hearing and independent tribunal requirements", "popularity": 95},
                    {"name": "De Cubber v Belgium (1984)", "significance": "Impartiality of judges and fair trial rights", "popularity": 89},
                    {"name": "R v UK (1989)", "significance": "Right to legal representation and defense", "popularity": 93},
                    {"name": "Edwards and Lewis v UK (2004)", "significance": "Right to fair trial and access to justice", "popularity": 88},
                    {"name": "Papon v France (2002)", "significance": "Public hearing requirements and fair procedures", "popularity": 85}
                ]
            },
            {
                "number": 11,
                "title": "Freedom of Assembly and Association",
                "content": "Everyone has the right to freedom of peaceful assembly and to freedom of association with others, including the right to form and to join trade unions for the protection of his interests.",
                "key_cases": [
                    {"name": "Steel and Others v UK (1998)", "significance": "Freedom of assembly and peaceful protest rights", "popularity": 92},
                    {"name": "Hashman and Harrup v UK (1999)", "significance": "Freedom of association and protest", "popularity": 87},
                    {"name": "Ezelin v France (1991)", "significance": "Assembly rights and police powers", "popularity": 84},
                    {"name": "Wilson and the National Union of Journalists v UK (2002)", "significance": "Trade union rights and freedom of association", "popularity": 91},
                    {"name": "Vogt v Germany (1995)", "significance": "Public service employment and freedom of association", "popularity": 79}
                ]
            },
            {
                "number": "P1-1",
                "title": "Protection of Property",
                "content": "Every natural or legal person is entitled to the peaceful enjoyment of his possessions. No one shall be deprived of his possessions except in the public interest and subject to the conditions provided for by law.",
                "key_cases": [
                    {"name": "James v UK (1986)", "significance": "Property rights and statutory leasehold reform", "popularity": 94},
                    {"name": "Air Canada v UK (1995)", "significance": "Property deprivation and public interest", "popularity": 89},
                    {"name": "Holy Monasteries v Greece (1999)", "significance": "Religious property and state interference", "popularity": 85},
                    {"name": "Buckley v UK (1996)", "significance": "Gipsy caravan sites and property rights", "popularity": 87},
                    {"name": "Grzelak v Poland (2010)", "significance": "Intellectual property and peaceful enjoyment", "popularity": 82},
                    {"name": "R (on the application of Lasserson) v Lambeth London Borough Council (2017)", "significance": "Housing rights and property possession", "popularity": 88}
                ]
            },
            {
                "number": "JI-1",
                "title": "Judicial Independence",
                "content": "The independence of the judiciary is fundamental to the rule of law and the protection of human rights. Courts must be free from improper influence and interference from the executive and legislature.",
                "key_cases": [
                    {"name": "R v Secretary of State for the Home Department, ex parte Fire Brigades' Union (1995)", "significance": "Judicial independence from executive interference", "popularity": 96},
                    {"name": "R (on the application of Miller) v Secretary of State for Exiting the European Union (2017)", "significance": "Supreme Court independence in constitutional matters", "popularity": 98},
                    {"name": "Anisminic Ltd v Foreign Compensation Commission (1969)", "significance": "Judicial review and administrative law independence", "popularity": 95},
                    {"name": "Council of Civil Service Unions v Minister for the Civil Service (1985)", "significance": "Judicial review scope and government accountability", "popularity": 92},
                    {"name": "R (on the application of PR) v Secretary of State for Justice (2011)", "significance": "Judicial appointments and independence safeguards", "popularity": 89},
                    {"name": "Burgess v Secretary of State for Defence (2015)", "significance": "Judicial independence in national security cases", "popularity": 86}
                ]
            }
        ]
    },
    "constitutional_conventions": {
        "articles": [
            {
                "number": 1,
                "title": "Parliamentary Sovereignty",
                "content": "Parliament is the supreme legal authority in the UK, which can create or end any law.",
                "key_cases": [
                    {"name": "R (on the application of Miller) v Secretary of State (2017)", "significance": "Parliamentary sovereignty vs EU law", "popularity": 96},
                    {"name": "Jackson v Attorney General (2005)", "significance": "Limits of parliamentary sovereignty", "popularity": 88},
                    {"name": "Thoburn v Sunderland City Council (2002)", "significance": "Constitutional statutes vs ordinary statutes", "popularity": 82}
                ]
            },
            {
                "number": 2,
                "title": "Rule of Law",
                "content": "The principle that all persons, institutions and entities are accountable to laws that are publicly promulgated, equally enforced.",
                "key_cases": [
                    {"name": "R v Secretary of State for the Home Department, ex p. Pierson (1998)", "significance": "Natural justice and fair procedures", "popularity": 87},
                    {"name": "Anisminic v Foreign Compensation Commission (1969)", "significance": "Judicial review of administrative action", "popularity": 92},
                    {"name": "Council of Civil Service Unions v Minister for the Civil Service (1985)", "significance": "Legitimate expectations", "popularity": 79}
                ]
            }
        ]
    },
    "devolution_acts": {
        "articles": [
            {
                "number": 1,
                "title": "Scottish Parliament Powers",
                "content": "The Scottish Parliament is the national legislature of Scotland.",
                "key_cases": [
                    {"name": "Cherry v Scottish Ministers (2019)", "significance": "Scottish Parliament powers and human rights", "popularity": 83},
                    {"name": "Martin v HMA (2016)", "significance": "Devolution and criminal law", "popularity": 76},
                    {"name": "AXA v Scottish Government (2021)", "significance": "Constitutional limits on devolved powers", "popularity": 74}
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

        # Select constitution data based on jurisdiction
        constitution_data = {
            "IN": INDIAN_CONSTITUTION,
            "UAE": UAE_CONSTITUTION,
            "UK": UK_CONSTITUTION
        }.get(jurisdiction)
        
        if not constitution_data:
            raise HTTPException(status_code=400, detail=f"Jurisdiction {jurisdiction} not supported. Supported jurisdictions: IN, UAE, UK")

        # If specific article requested
        if request.article_number:
            for category, data in constitution_data.items():
                for article in data["articles"]:
                    if article["number"] == request.article_number:
                        # Track article view
                        save_article_interaction(str(article["number"]), jurisdiction, "view")
                        
                        # Get popular articles for context
                        popular_articles_data = get_popular_articles(jurisdiction, limit=3)
                        trending_topics = get_trending_topics(jurisdiction)
                        
                        court_name = "Supreme Court of India" if jurisdiction == "IN" else "Federal Court" if jurisdiction == "UAE" else "UK Supreme Court"
                        return ConstitutionResponse(
                            articles=[article],
                            relevant_sections=[],
                            interpretation=f"Article {article['number']} - {article['title']}: {article['content'][:100]}...",
                            case_law=[{"case": case["name"], "year": case["name"].split('(')[-1].split(')')[0] if '(' in case["name"] else "Historical", "court": court_name} for case in article["key_cases"]],
                            amendments=[],
                            popular_articles=[],
                            trending_topics=trending_topics
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
        
        # Enhanced Jurisdiction-specific keyword mapping
        legal_keywords = {
            "IN": {
                "equality": {"articles": ["14", "15", "16", "17", "18"], "cases": ["kesavananda", "maneka", "sabarimala", "transgender"]},
                "speech": {"articles": ["19"], "cases": ["shreya", "bennett", "ka abbas"]},
                "liberty": {"articles": ["21", "22"], "cases": ["puttaswamy", "vishaka", "maneka"]},
                "religion": {"articles": ["25", "26", "27", "28"], "cases": ["sabarimala", "shah bano"]},
                "remedies": {"articles": ["32"], "cases": ["vishaka", "bandhua", "kesavananda"]},
                "women": {"articles": ["14", "15", "39", "42"], "cases": ["sabarimala", "vishaka"]},
                "privacy": {"articles": ["21"], "cases": ["puttaswamy"]},
                "harassment": {"articles": ["21"], "cases": ["vishaka"]},
                "reservation": {"articles": ["14", "15", "16"], "cases": ["thomas", "kesavananda"]},
                "education": {"articles": ["21A", "41"], "cases": ["unni krishnan"]},
                "discrimination": {"articles": ["14", "15", "16"], "cases": ["kesavananda", "thomas"]},
                "due_process": {"articles": ["21"], "cases": ["maneka", "puttaswamy"]}
            },
            "UAE": {
                "equality": {"articles": ["25", "40"], "cases": ["dubai", "abu dhabi", "emirates court", "women", "gender"]},
                "liberty": {"articles": ["31"], "cases": ["federal supreme", "emirates court", "due process"]},
                "speech": {"articles": ["32"], "cases": ["press freedom", "media court", "expression"]},
                "rule": {"articles": ["45", "50"], "cases": ["rule of law", "federal court", "judicial review", "independence"]},
                "family": {"articles": ["14"], "cases": ["family court", "personal status", "marriage"]},
                "freedom": {"articles": ["32"], "cases": ["media freedom", "press rights", "expression"]},
                "detention": {"articles": ["31"], "cases": ["arrest procedures", "due process", "federal court"]},
                "federal": {"articles": ["1"], "cases": ["federal authority", "supreme court", "emirates"]},
                "discrimination": {"articles": ["25", "40"], "cases": ["gender equality", "employment rights", "citizenship", "women", "equal pay"]},
                "privacy": {"articles": ["10", "31"], "cases": ["privacy rights", "personal liberty", "emirates court"]},
                "criminal": {"articles": ["31"], "cases": ["criminal procedure", "fair trial", "federal supreme"]},
                "social": {"articles": ["10"], "cases": ["social rights", "family protection", "decent living"]},
                "women": {"articles": ["40"], "cases": ["gender equality", "workplace", "leadership", "political participation"]},
                "judicial": {"articles": ["50"], "cases": ["independence", "impartiality", "separation of powers", "judges"]},
                "property": {"articles": ["60"], "cases": ["private property", "expropriation", "compensation", "ownership"]},
                "education": {"articles": ["33"], "cases": ["compulsory education", "free access", "literacy", "higher education"]},
                "economic": {"articles": ["20"], "cases": ["livelihood", "social security", "health insurance", "employment"]},
                "independence": {"articles": ["50"], "cases": ["judicial independence", "executive interference", "impartial"]}
            },
            "UK": {
                "privacy": {"articles": ["8"], "cases": ["campbell", "pretty", "s", "khorasandjian"]},
                "liberty": {"articles": ["4"], "cases": ["murray", "worm", "detention", "legal representation"]},
                "speech": {"articles": ["10"], "cases": ["handyside", "newspaper licensing", "expression", "political"]},
                "torture": {"articles": ["3"], "cases": ["chahal", "soering", "inhuman", "degrading"]},
                "life": {"articles": ["2"], "cases": ["pretty", "hill", "campbell", "assisted suicide"]},
                "equality": {"articles": ["1"], "cases": ["gillan", "bank mellat", "convention rights", "-discrimination"]},
                "religion": {"articles": ["9"], "cases": ["siddiqui", "thorn", "religious freedom", "conscience"]},
                "parliamentary": {"articles": ["1"], "cases": ["miller", "jackson", "thoburn", "sovereignty", "brexit"]},
                "rule_of_law": {"articles": ["2"], "cases": ["anisminic", "council of civil service", "natural justice", "fair procedures"]},
                "devolution": {"articles": ["1"], "cases": ["cherry", "martin", "axa", "scottish parliament", "welsh assembly"]},
                "fair_trial": {"articles": ["6"], "cases": ["fair hearing", "independent tribunal", "procedural rights", "barberà", "edwards"]},
                "assembly": {"articles": ["11"], "cases": ["freedom of assembly", "peaceful protest", "demonstration", "steel"]},
                "association": {"articles": ["11"], "cases": ["freedom of association", "trade unions", "collective action", "wilson"]},
                "property": {"articles": ["P1-1"], "cases": ["property rights", "possession", "peaceful enjoyment", "james", "air canada"]},
                "property_rights": {"articles": ["P1-1"], "cases": ["property rights", "peaceful enjoyment", "expropriation", "compensation"]},
                "compensation": {"articles": ["P1-1"], "cases": ["expropriation", "public interest", "compensation", "deprivation"]},
                "peaceful": {"articles": ["P1-1"], "cases": ["peaceful enjoyment", "possession", "property"]},
                "enjoyment": {"articles": ["P1-1"], "cases": ["peaceful enjoyment", "property", "possessions"]},
                "security": {"articles": ["1", "2", "3", "4"], "cases": ["national security", "public safety", "counter-terrorism"]},
                "brexit": {"articles": ["1"], "cases": ["miller", "withdrawal", "eu law", "parliamentary sovereignty"]},
                "judicial": {"articles": ["JI-1"], "cases": ["independence", "executive interference", "impartial", "anisminic", "miller"]},
                "independence": {"articles": ["JI-1"], "cases": ["judicial independence", "separation of powers", "fire brigades", "burgess"]},
                "tribunal": {"articles": ["6"], "cases": ["independent tribunal", "fair hearing", "procedural", "public hearing"]},
                "protest": {"articles": ["11"], "cases": ["peaceful assembly", "protest rights", "steel", "hashman"]},
                "trade_union": {"articles": ["11"], "cases": ["wilson", "trade unions", "collective action", "association"]},
                "hearing": {"articles": ["6"], "cases": ["fair hearing", "public hearing", "reasonable time", "edwards"]}
            }
        }
        
        # Get jurisdiction-specific keywords
        current_keywords = legal_keywords.get(jurisdiction, legal_keywords["IN"])
        
        # Analyze query for legal topics using jurisdiction-specific keywords
        # Enhanced matching: require stronger connections
        for topic, data in current_keywords.items():
            topic_words = topic.split()
            # Count how many words from the topic appear in the query
            matching_words = sum(1 for word in topic_words if word in query_lower)
            
            # Require at least one word match, or multiple word matches for compound topics
            if (matching_words >= 1 and len(topic_words) == 1) or (matching_words >= 2 and len(topic_words) > 1):
                query_analysis["detected_topics"].append(topic)
                
                # Add relevant articles with boosted relevance score
                relevance_boost = matching_words  # Higher boost for better matches
                for article_num in data["articles"]:
                    query_analysis["article_relevance"][article_num] = query_analysis["article_relevance"].get(article_num, 0) + relevance_boost
                
                # Add relevant case keywords
                query_analysis["case_keywords"].extend(data["cases"])
        
        # Check for case name matches across all categories
        case_matches = []
        for category, data in constitution_data.items():
            for article in data["articles"]:
                for case_obj in article.get("key_cases", []):
                    case_name_lower = case_obj["name"].lower()
                    if any(keyword in query_lower for keyword in case_obj["name"].lower().split()):
                        case_matches.append({
                            "case": case_obj,
                            "article": article,
                            "match_type": "case_name"
                        })
        
        # Check for article number matches across all categories
        article_matches = []
        for category, data in constitution_data.items():
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
            article_str = str(match["article"]["number"])
            if article_str not in [str(x) for x in seen_articles]:
                matching_articles.append(match["article"])
                seen_articles.add(match["article"]["number"])
        
        # Then add article number matches
        for match in article_matches:
            article_str = str(match["article"]["number"])
            if article_str not in [str(x) for x in seen_articles]:
                matching_articles.append(match["article"])
                seen_articles.add(match["article"]["number"])
        
        # Add articles based on topic relevance using dynamic constitution data
        # Only include articles with relevance score >= 2 to ensure direct relevance
        for article_num, relevance_score in query_analysis["article_relevance"].items():
            if relevance_score >= 2:  # Higher threshold for direct relevance
                for category, data in constitution_data.items():
                    for article in data["articles"]:
                        article_str = str(article["number"])
                        if article_str == article_num and article_str not in [str(x) for x in seen_articles]:
                            matching_articles.append(article)
                            seen_articles.add(article["number"])
                            break
        
        # If no specific matches, return most relevant general articles based on jurisdiction
        # But only if we have some detected topics to indicate relevance
        if not matching_articles and query_analysis["detected_topics"]:
            # Enhanced Jurisdiction-specific fallback article selection
            if jurisdiction == "IN":
                fallback_mapping = {
                    "free": 19, "speech": 19, "expression": 19, "media": 19,
                    "equal": 14, "discrimination": 14, "fair": 14, "justice": 14,
                    "life": 21, "liberty": 21, "privacy": 21, "right": 21, "personal": 21,
                    "religion": 25, "religious": 25, "temple": 25, "faith": 25, "worship": 25,
                    "remedy": 32, "writ": 32, "constitutional": 32, "enforcement": 32, "supreme court": 32
                }
                default_articles = [14, 19, 21]
            elif jurisdiction == "UAE":
                fallback_mapping = {
                    "equality": 25, "discrimination": 25, "equal": 25, "gender": 25,
                    "liberty": 31, "freedom": 31, "detention": 31, "arrest": 31, "personal": 31,
                    "speech": 32, "expression": 32, "press": 32, "media": 32, "opinion": 32,
                    "rule": 45, "law": 45, "judicial": 50, "federal": 45,
                    "family": 14, "marriage": 14, "social": 10, "citizen": 10, "decent": 10,
                    "constitution": 1, "state": 1, "sovereign": 1, "territory": 1,
                    "privacy": 10, "individual": 10, "rights": 10, "fundamental": 10,
                    "criminal": 31, "procedure": 31, "due process": 31, "court": 50,
                    "federal": 1, "supreme": 1, "emirate": 1, "authority": 1,
                    "women": 40, "gender equality": 40, "workplace": 40, "leadership": 40,
                    "education": 33, "educational": 33, "literacy": 33, "school": 33,
                    "economic": 20, "economic security": 20, "livelihood": 20, "employment": 20,
                    "property": 60, "ownership": 60, "compensation": 60, "expropriation": 60,
                    "independence": 50, "judicial independence": 50, "judges": 50, "impartial": 50
                }
                default_articles = [1, 10, 25, 31, 40]
            elif jurisdiction == "UK":
                fallback_mapping = {
                    "privacy": 8, "private": 8, "home": 8, "correspondence": 8, "family life": 8,
                    "liberty": 4, "detention": 4, "security": 4, "freedom": 4,
                    "torture": 3, "inhuman": 3, "degrading": 3, "treatment": 3,
                    "speech": 10, "expression": 10, "opinion": 10, "information": 10, "media": 10,
                    "life": 2, "death": 2, "assisted suicide": 2, "torture evidence": 2,
                    "religion": 9, "thought": 9, "conscience": 9, "belief": 9, "religious": 9,
                    "parliamentary": 1, "sovereignty": 1, "parliament": 1, "eu": 1, "brexit": 1,
                    "rule of law": 2, "fair": 2, "justice": 2, "administrative": 2,
                    "human rights": 1, "convention": 1, "echr": 1, "european": 1,
                    "fair trial": 6, "hearing": 6, "tribunal": 6, "procedural": 6, "public hearing": 6,
                    "assembly": 11, "protest": 11, "demonstration": 11, "peaceful": 11,
                    "association": 11, "trade union": 11, "collective": 11,
                    "discrimination": 1, "equal": 1, "treatment": 1,
                    "property": "P1-1", "possession": "P1-1", "enjoyment": "P1-1", "wealth": "P1-1", "expropriation": "P1-1",
                    "security": 2, "national": 2, "public": 2, "safety": 2,
                    "devolution": 1, "scotland": 1, "wales": 1, "northern ireland": 1,
                    "judicial": "JI-1", "independence": "JI-1", "impartial": "JI-1", "judges": "JI-1",
                    "compensation": "P1-1", "deprivation": "P1-1", "peaceful enjoyment": "P1-1"
                }
                default_articles = [1, 2, 8, 6]
            
            # Find matching article or use default
            article_number = None
            for keyword, num in fallback_mapping.items():
                if any(word in query_lower for word in keyword.split()):
                    article_number = num
                    break
            
            if article_number:
                for category, data in constitution_data.items():
                    for article in data["articles"]:
                        if str(article["number"]) == str(article_number):
                            matching_articles = [article]
                            break
            else:
                # Return default articles for the jurisdiction
                matching_articles = []
                default_article_strs = [str(x) for x in default_articles]
                for category, data in constitution_data.items():
                    for article in data["articles"]:
                        if str(article["number"]) in default_article_strs and str(article["number"]) not in [str(a["number"]) for a in matching_articles]:
                            matching_articles.append(article)
                            if len(matching_articles) >= 3:
                                break
                    if len(matching_articles) >= 3:
                        break
        
        # Limit to most relevant articles (max 3) but ensure diversity
        seen_numbers = set()
        diverse_articles = []
        for article in matching_articles:
            article_str = str(article["number"])
            if article_str not in seen_numbers:
                diverse_articles.append(article)
                seen_numbers.add(article_str)
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
        
        # Interpretation based on query analysis with jurisdiction context
        # Define jurisdiction_name at the beginning for consistent use
        jurisdiction_name = {"IN": "India", "UAE": "UAE", "UK": "United Kingdom"}[jurisdiction]
        
        if matching_articles:
            primary_article = matching_articles[0]
            
            # Customized interpretation based on query analysis and jurisdiction
            if query_analysis["detected_topics"]:
                topic_list = ", ".join(query_analysis["detected_topics"])
                interpretation = f"Your query relates to {topic_list}. Article {primary_article['number']} ({primary_article['title']}) is particularly relevant under {jurisdiction_name} law. "
                
                # Jurisdiction-specific interpretations
                if jurisdiction == "IN":
                    if "speech" in query_analysis["detected_topics"]:
                        interpretation += "The Supreme Court of India has interpreted free speech to include reasonable restrictions for public order, morality, and the rights of others."
                    elif "equality" in query_analysis["detected_topics"]:
                        interpretation += "The right to equality has been expanded to include not just formal equality but also substantive equality in practice."
                    elif "liberty" in query_analysis["detected_topics"]:
                        interpretation += "Personal liberty has been interpreted broadly to include privacy, dignity, and various aspects of human development."
                    elif "religion" in query_analysis["detected_topics"]:
                        interpretation += "Religious freedom includes both individual and collective rights, subject to reasonable restrictions."
                elif jurisdiction == "UAE":
                    if "liberty" in query_analysis["detected_topics"]:
                        interpretation += "The Federal Supreme Court has established due process protections and limitations on detention."
                    elif "rule" in query_analysis["detected_topics"]:
                        interpretation += "The rule of law is a fundamental principle with judicial review mechanisms established by federal courts."
                    elif "family" in query_analysis["detected_topics"]:
                        interpretation += "Family law emphasizes traditional values while protecting individual rights within the UAE framework."
                elif jurisdiction == "UK":
                    if "privacy" in query_analysis["detected_topics"]:
                        interpretation += "The UK courts have developed extensive privacy protections under the Human Rights Act 1998."
                    elif "torture" in query_analysis["detected_topics"]:
                        interpretation += "The prohibition of torture is absolute under Article 3 ECHR with no exceptions."
                    elif "speech" in query_analysis["detected_topics"]:
                        interpretation += "Freedom of expression is balanced against public order, national security, and individual rights."
                    elif "parliamentary" in query_analysis["detected_topics"]:
                        interpretation += "Parliamentary sovereignty remains the cornerstone of UK constitutional law."
            else:
                court_name = {"IN": "Supreme Court", "UAE": "Federal Supreme Court", "UK": "UK Supreme Court"}[jurisdiction]
                interpretation = f"Article {primary_article['number']} guarantees {primary_article['title'].lower()} under {jurisdiction_name} law. This provision has been interpreted by the {court_name} to include various dimensions and reasonable restrictions."
        else:
            interpretation = f"Your query touches upon constitutional principles under {jurisdiction_name} law. Based on the detected topics ({', '.join(query_analysis['detected_topics'])}), you may want to explore the constitutional framework more specifically."

        # Enhanced case law with jurisdiction-specific court information
        case_law = []
        for article in matching_articles[:2]:  # Limit to 2 articles
            for case_obj in article.get("key_cases", [])[:2]:  # Max 2 cases per article
                court_name = {
                    "IN": "Supreme Court of India",
                    "UAE": "Federal Supreme Court UAE", 
                    "UK": "UK Supreme Court"
                }.get(jurisdiction, "Constitutional Court")
                
                case_law.append({
                    "case": case_obj["name"],
                    "year": case_obj["name"].split('(')[-1].split(')')[0] if '(' in case_obj["name"] else "Historical",
                    "court": court_name,
                    "significance": case_obj.get("significance", "Constitutional interpretation"),
                    "relevance_score": case_obj.get("popularity", 75)
                })

        # Dynamic amendments based on query topics and jurisdiction
        amendments = []
        
        if jurisdiction == "IN":
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
        
        elif jurisdiction == "UAE":
            if "family" in query_analysis["detected_topics"]:
                amendments.append({
                    "number": 1,
                    "year": 1974,
                    "description": "Federal Structure",
                    "relevance": "Established federal authority over personal status matters"
                })
            if "rule" in query_analysis["detected_topics"]:
                amendments.append({
                    "number": 2,
                    "year": 1996,
                    "description": "Judicial System Enhancement",
                    "relevance": "Strengthened rule of law principles in federal jurisdiction"
                })
        
        elif jurisdiction == "UK":
            if "human_rights" in query_analysis["detected_topics"]:
                amendments.append({
                    "number": 1,
                    "year": 1998,
                    "description": "Human Rights Act",
                    "relevance": "Incorporated European Convention on Human Rights into UK law"
                })
            if "devolution" in query_analysis["detected_topics"]:
                amendments.append({
                    "number": 1,
                    "year": 1998,
                    "description": "Scotland Act",
                    "relevance": "Established Scottish Parliament and devolved powers"
                })
        
        # Default amendments if none specific - jurisdiction specific
        if not amendments:
            if jurisdiction == "IN":
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
            elif jurisdiction == "UAE":
                amendments = [
                    {
                        "number": 1,
                        "year": 1971,
                        "description": "Constitution Promulgation",
                        "relevance": "Established the foundational constitutional framework"
                    },
                    {
                        "number": 2,
                        "year": 1996,
                        "description": "Federal System Strengthening",
                        "relevance": "Enhanced federal structure and judicial powers"
                    }
                ]
            elif jurisdiction == "UK":
                amendments = [
                    {
                        "number": 1,
                        "year": 1998,
                        "description": "Human Rights Act",
                        "relevance": "Modernized rights framework under European Convention"
                    },
                    {
                        "number": 1,
                        "year": 2005,
                        "description": "Constitutional Reform Act",
                        "relevance": "Established Supreme Court and reformed House of Lords"
                    }
                ]

        # Track article interactions for popularity
        for article in matching_articles:
            save_article_interaction(str(article["number"]), jurisdiction, "search")
        
        # Get popular articles and trending topics
        popular_articles_data = get_popular_articles(jurisdiction, limit=5)
        trending_topics = get_trending_topics(jurisdiction)
        
        # Convert popular articles data to article objects
        popular_articles = []
        for pop_data in popular_articles_data:
            # Find the actual article object
            for category, data in constitution_data.items():
                for article in data["articles"]:
                    if str(article["number"]) == pop_data["article_number"]:
                        article_copy = article.copy()
                        article_copy["popularity_stats"] = {
                            "total_interactions": pop_data["total_interactions"],
                            "views": pop_data["views"],
                            "searches": pop_data["searches"],
                            "clicks": pop_data["clicks"],
                            "trend_score": round(pop_data["trend_score"], 2),
                            "last_accessed": pop_data["last_accessed"]
                        }
                        popular_articles.append(article_copy)
                        break
                if popular_articles and popular_articles[-1]["number"] == pop_data["article_number"]:
                    break
        
        return ConstitutionResponse(
            articles=matching_articles,
            relevant_sections=relevant_sections,
            interpretation=interpretation,
            popular_cases=popular_cases,
            case_law=case_law,
            amendments=amendments,
            query_analysis=query_analysis,
            popular_articles=popular_articles,
            trending_topics=trending_topics
        )

    except Exception as e:
        logger.error(f"Constitution search error: {str(e)}")
        raise HTTPException(status_code=500, detail="Constitution search failed")


@router.post("/track-article")
async def track_article_interaction(request: PopularityTrackingRequest):
    """Track user interactions with constitutional articles"""
    try:
        save_article_interaction(request.article_number, request.jurisdiction, request.action)
        return {"status": "success", "message": "Interaction tracked"}
    except Exception as e:
        logger.error(f"Error tracking article interaction: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to track interaction")


@router.get("/popular-articles")
async def get_popular_constitutional_articles(
    jurisdiction: str = "IN", 
    limit: int = 5
):
    """Get most popular constitutional articles based on user engagement"""
    try:
        if jurisdiction.upper() not in ["IN", "UAE", "UK"]:
            raise HTTPException(status_code=400, detail="Unsupported jurisdiction")
        
        popular_articles_data = get_popular_articles(jurisdiction.upper(), limit)
        
        # Convert to response format
        constitution_data = {
            "IN": INDIAN_CONSTITUTION,
            "UAE": UAE_CONSTITUTION,
            "UK": UK_CONSTITUTION
        }[jurisdiction.upper()]
        
        popular_articles = []
        for pop_data in popular_articles_data:
            for category, data in constitution_data.items():
                for article in data["articles"]:
                    if str(article["number"]) == pop_data["article_number"]:
                        article_copy = article.copy()
                        article_copy["popularity_stats"] = {
                            "total_interactions": pop_data["total_interactions"],
                            "views": pop_data["views"],
                            "searches": pop_data["searches"],
                            "clicks": pop_data["clicks"],
                            "trend_score": round(pop_data["trend_score"], 2),
                            "last_accessed": pop_data["last_accessed"],
                            "rank": len(popular_articles) + 1
                        }
                        popular_articles.append(article_copy)
                        break
                if popular_articles and popular_articles[-1]["number"] == pop_data["article_number"]:
                    break
        
        return {
            "jurisdiction": jurisdiction.upper(),
            "popular_articles": popular_articles,
            "total_tracked": len(popular_articles_data),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting popular articles: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get popular articles")


@router.get("/trending-topics")
async def get_constitution_trending_topics(jurisdiction: str = "IN"):
    """Get trending constitutional topics based on recent user searches"""
    try:
        if jurisdiction.upper() not in ["IN", "UAE", "UK"]:
            raise HTTPException(status_code=400, detail="Unsupported jurisdiction")
        
        trending_topics = get_trending_topics(jurisdiction.upper())
        
        # Get popularity data for context
        popularity_data = load_article_popularity()
        
        return {
            "jurisdiction": jurisdiction.upper(),
            "trending_topics": trending_topics,
            "total_interactions": sum(
                data['total_interactions'] for data in popularity_data.values() 
                if data['jurisdiction'] == jurisdiction.upper()
            ),
            "active_articles": len([
                data for data in popularity_data.values()
                if data['jurisdiction'] == jurisdiction.upper() and data['total_interactions'] > 0
            ]),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting trending topics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get trending topics")


@router.get("/analytics")
async def get_constitution_analytics(jurisdiction: str = "IN"):
    """Get comprehensive analytics for constitutional article usage"""
    try:
        popularity_data = load_article_popularity()
        jurisdiction_data = [
            data for data in popularity_data.values() 
            if data['jurisdiction'] == jurisdiction.upper()
        ]
        
        # Calculate analytics
        total_interactions = sum(data['total_interactions'] for data in jurisdiction_data)
        total_views = sum(data['views'] for data in jurisdiction_data)
        total_searches = sum(data['searches'] for data in jurisdiction_data)
        total_clicks = sum(data['clicks'] for data in jurisdiction_data)
        
        # Top articles by different metrics
        top_by_interactions = sorted(jurisdiction_data, key=lambda x: x['total_interactions'], reverse=True)[:3]
        top_by_views = sorted(jurisdiction_data, key=lambda x: x['views'], reverse=True)[:3]
        top_by_searches = sorted(jurisdiction_data, key=lambda x: x['searches'], reverse=True)[:3]
        
        # Activity timeline (last 7 days)
        activity_timeline = []
        for i in range(7):
            date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
            day_str = date.strftime("%Y-%m-%d")
            
            day_interactions = 0
            try:
                if POPULARITY_FILE.exists():
                    with open(POPULARITY_FILE, 'r') as f:
                        for line in f:
                            if line.strip():
                                data = json.loads(line)
                                if (data['jurisdiction'] == jurisdiction.upper() and 
                                    data.get('timestamp') and
                                    data['timestamp'][:10] == day_str):
                                    day_interactions += 1
            except:
                pass
            
            activity_timeline.append({
                "date": day_str,
                "interactions": day_interactions
            })
        
        return {
            "jurisdiction": jurisdiction.upper(),
            "summary": {
                "total_interactions": total_interactions,
                "total_views": total_views,
                "total_searches": total_searches,
                "total_clicks": total_clicks,
                "active_articles": len([d for d in jurisdiction_data if d['total_interactions'] > 0])
            },
            "top_articles": {
                "by_interactions": [
                    {"article_number": data["article_number"], "interactions": data["total_interactions"]}
                    for data in top_by_interactions
                ],
                "by_views": [
                    {"article_number": data["article_number"], "views": data["views"]}
                    for data in top_by_views
                ],
                "by_searches": [
                    {"article_number": data["article_number"], "searches": data["searches"]}
                    for data in top_by_searches
                ]
            },
            "activity_timeline": activity_timeline,
            "trending_topics": get_trending_topics(jurisdiction.upper()),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")
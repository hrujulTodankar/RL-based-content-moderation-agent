#!/usr/bin/env python3
"""
Jurisdiction-Aware Content Processing
====================================

Implements context-aware processing with jurisdiction-specific analysis rules
for legal content moderation across multiple legal systems.

Author: Content Moderation System
Version: 1.0.0
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from .api_wrappers import APIException, APIErrorCodes

logger = logging.getLogger(__name__)

class JurisdictionContext:
    """Context information for jurisdiction-aware processing"""
    
    def __init__(self, country_code: str = "IN"):
        self.country_code = country_code.upper()
        self.legal_system = self._get_legal_system()
        self.language_preferences = self._get_language_preferences()
        self.cultural_context = self._get_cultural_context()
        self.legal_frameworks = self._get_legal_frameworks()
    
    def _get_legal_system(self) -> str:
        """Get legal system type for jurisdiction"""
        systems = {
            "IN": "common_law_with_civil_influences",
            "UK": "common_law",
            "US": "common_law",
            "UAE": "civil_law_with_islamic_influences",
            "FR": "civil_law",
            "DE": "civil_law"
        }
        return systems.get(self.country_code, "unknown")
    
    def _get_language_preferences(self) -> Dict[str, Any]:
        """Get language preferences for jurisdiction"""
        preferences = {
            "IN": {
                "primary": ["en", "hi", "bn", "ta", "te", "mr", "gu", "kn", "ml", "pa"],
                "legal_language": ["en", "hi"],
                "script_preferences": ["latin", "devanagari"]
            },
            "UK": {
                "primary": ["en"],
                "legal_language": ["en"],
                "script_preferences": ["latin"]
            },
            "US": {
                "primary": ["en", "es"],
                "legal_language": ["en"],
                "script_preferences": ["latin"]
            },
            "UAE": {
                "primary": ["ar", "en"],
                "legal_language": ["ar"],
                "script_preferences": ["arabic", "latin"]
            }
        }
        return preferences.get(self.country_code, {"primary": ["en"], "legal_language": ["en"], "script_preferences": ["latin"]})
    
    def _get_cultural_context(self) -> Dict[str, Any]:
        """Get cultural context for jurisdiction"""
        contexts = {
            "IN": {
                "formality_level": "high",
                "religious_sensitivity": "high",
                "family_values": "important",
                "respect_hierarchy": "important",
                "directness": "moderate"
            },
            "UK": {
                "formality_level": "high",
                "religious_sensitivity": "moderate",
                "family_values": "moderate",
                "respect_hierarchy": "important",
                "directness": "moderate"
            },
            "US": {
                "formality_level": "moderate",
                "religious_sensitivity": "moderate",
                "family_values": "important",
                "respect_hierarchy": "low",
                "directness": "high"
            },
            "UAE": {
                "formality_level": "very_high",
                "religious_sensitivity": "very_high",
                "family_values": "very_important",
                "respect_hierarchy": "very_important",
                "directness": "low"
            }
        }
        return contexts.get(self.country_code, contexts["IN"])
    
    def _get_legal_frameworks(self) -> Dict[str, Any]:
        """Get legal framework information for jurisdiction"""
        frameworks = {
            "IN": {
                "constitution": "Constitution of India",
                "penal_code": "Bharatiya Nyaya Sanhita (BNS) 2023",
                "criminal_procedure": "Bharatiya Nagarik Suraksha Sanhita (BNSS) 2023",
                "civil_procedure": "Code of Civil Procedure",
                "contract_law": "Indian Contract Act",
                "family_law": "Personal laws by religion",
                "corporate_law": "Companies Act"
            },
            "UK": {
                "constitution": "Constitutional conventions",
                "penal_code": "Various Acts",
                "criminal_procedure": "Police and Criminal Evidence Act",
                "civil_procedure": "Civil Procedure Rules",
                "contract_law": "Common law principles",
                "family_law": "Matrimonial Causes Act",
                "corporate_law": "Companies Act 2006"
            },
            "US": {
                "constitution": "US Constitution",
                "penal_code": "State penal codes",
                "criminal_procedure": "Federal Rules of Criminal Procedure",
                "civil_procedure": "Federal Rules of Civil Procedure",
                "contract_law": "UCC and common law",
                "family_law": "State family laws",
                "corporate_law": "State corporation laws"
            },
            "UAE": {
                "constitution": "Federal Constitution",
                "penal_code": "Federal Penal Code",
                "criminal_procedure": "Federal Criminal Procedure Law",
                "civil_procedure": "Civil Procedure Law",
                "contract_law": "Civil Code",
                "family_law": "Personal Status Law",
                "corporate_law": "Commercial Companies Law"
            }
        }
        return frameworks.get(self.country_code, frameworks["IN"])

class JurisdictionAnalyzer:
    """Jurisdiction-aware content analyzer"""
    
    def __init__(self):
        self.jurisdiction_contexts: Dict[str, JurisdictionContext] = {}
        self.sensitive_topics = self._initialize_sensitive_topics()
        self.jurisdiction_rules = self._initialize_jurisdiction_rules()
    
    def _initialize_sensitive_topics(self) -> Dict[str, Dict[str, Any]]:
        """Initialize jurisdiction-specific sensitive topics"""
        return {
            "IN": {
                "religious_content": {
                    "keywords": ["hindu", "muslim", "christian", "sikh", "buddhist", "jain", "parsee"],
                    "sensitivity": "high",
                    "description": "Religious harmony and communal content"
                },
                "caste_content": {
                    "keywords": ["brahmin", "kshatriya", "vaishya", "shudra", "dalit", "obc", "sc", "st"],
                    "sensitivity": "very_high",
                    "description": "Caste-related discrimination"
                },
                "political_content": {
                    "keywords": ["bjp", "congress", "aap", "communist", "secular", "nationalist"],
                    "sensitivity": "high",
                    "description": "Political party and ideology content"
                },
                "regional_content": {
                    "keywords": ["kashmir", "punjab", "assam", "tamil nadu", "kerala", "bengal"],
                    "sensitivity": "moderate",
                    "description": "Regional politics and separatist content"
                }
            },
            "UK": {
                "religious_content": {
                    "keywords": ["christian", "muslim", "jewish", "hindu", "sikh"],
                    "sensitivity": "high",
                    "description": "Religious harmony and discrimination"
                },
                "political_content": {
                    "keywords": ["brexit", "tory", "labour", "liberal democrat", "scottish national party"],
                    "sensitivity": "moderate",
                    "description": "Political party and Brexit content"
                },
                "historical_content": {
                    "keywords": ["empire", "colonial", "northern ireland", "scotland", "wales"],
                    "sensitivity": "moderate",
                    "description": "Historical and territorial content"
                }
            },
            "US": {
                "religious_content": {
                    "keywords": ["christian", "muslim", "jewish", "hindu", "buddhist"],
                    "sensitivity": "high",
                    "description": "Religious freedom and discrimination"
                },
                "political_content": {
                    "keywords": ["republican", "democrat", "libertarian", "socialist", "progressive", "conservative"],
                    "sensitivity": "very_high",
                    "description": "Political party and ideological content"
                },
                "race_content": {
                    "keywords": ["black", "white", "asian", "hispanic", "latino", "native american"],
                    "sensitivity": "very_high",
                    "description": "Racial equality and discrimination"
                },
                "guns_content": {
                    "keywords": ["gun", "weapon", "firearm", "rifle", "pistol", "second amendment"],
                    "sensitivity": "very_high",
                    "description": "Gun rights and control"
                }
            },
            "UAE": {
                "religious_content": {
                    "keywords": ["islam", "muslim", "christian", "jewish", "hindu"],
                    "sensitivity": "very_high",
                    "description": "Religious content in Islamic context"
                },
                "cultural_content": {
                    "keywords": ["tradition", "culture", "heritage", "emirati", "arab"],
                    "sensitivity": "high",
                    "description": "Cultural and traditional values"
                },
                "political_content": {
                    "keywords": ["government", "ruler", "emirate", "federal", "authority"],
                    "sensitivity": "high",
                    "description": "Government and authority content"
                }
            }
        }
    
    def _initialize_jurisdiction_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize jurisdiction-specific analysis rules"""
        return {
            "IN": {
                "scoring_adjustments": {
                    "religious_keywords": 0.3,
                    "caste_keywords": 0.5,
                    "political_keywords": 0.2,
                    "regional_keywords": 0.15
                },
                "content_restrictions": {
                    "defamation": "strict",
                    "hate_speech": "very_strict",
                    "obscenity": "strict",
                    "sedition": "very_strict"
                },
                "cultural_considerations": {
                    "formality_required": True,
                    "hierarchy_awareness": True,
                    "family_values_important": True
                }
            },
            "UK": {
                "scoring_adjustments": {
                    "religious_keywords": 0.2,
                    "political_keywords": 0.25,
                    "historical_keywords": 0.15
                },
                "content_restrictions": {
                    "defamation": "strict",
                    "hate_speech": "very_strict",
                    "obscenity": "moderate",
                    "privacy_violations": "strict"
                },
                "cultural_considerations": {
                    "formality_required": True,
                    "humor_acceptance": "moderate",
                    "directness_acceptable": False
                }
            },
            "US": {
                "scoring_adjustments": {
                    "religious_keywords": 0.2,
                    "political_keywords": 0.4,
                    "race_keywords": 0.5,
                    "gun_keywords": 0.4
                },
                "content_restrictions": {
                    "defamation": "strict",
                    "hate_speech": "very_strict",
                    "obscenity": "moderate",
                    "privacy_violations": "strict"
                },
                "cultural_considerations": {
                    "directness_acceptable": True,
                    "individualism_important": True,
                    "free_speech_priority": True
                }
            },
            "UAE": {
                "scoring_adjustments": {
                    "religious_keywords": 0.5,
                    "cultural_keywords": 0.3,
                    "political_keywords": 0.4
                },
                "content_restrictions": {
                    "defamation": "very_strict",
                    "hate_speech": "very_strict",
                    "obscenity": "very_strict",
                    "religious_criticism": "very_strict",
                    "cultural_criticism": "very_strict"
                },
                "cultural_considerations": {
                    "formality_required": True,
                    "hierarchy_awareness": True,
                    "cultural_sensitivity_essential": True,
                    "religious_sensitivity_essential": True
                }
            }
        }
    
    def get_context(self, country_code: str) -> JurisdictionContext:
        """Get or create jurisdiction context"""
        if country_code.upper() not in self.jurisdiction_contexts:
            self.jurisdiction_contexts[country_code.upper()] = JurisdictionContext(country_code)
        return self.jurisdiction_contexts[country_code.upper()]
    
    def analyze_content_jurisdiction(
        self, 
        content: str, 
        country_code: str = "IN",
        content_type: str = "text"
    ) -> Dict[str, Any]:
        """
        Analyze content with jurisdiction-specific rules
        
        Args:
            content: Content to analyze
            country_code: Jurisdiction country code
            content_type: Type of content
            
        Returns:
            Analysis results with jurisdiction-specific scoring
        """
        try:
            context = self.get_context(country_code)
            analysis_result = {
                "country_code": country_code,
                "content_type": content_type,
                "timestamp": datetime.utcnow().isoformat(),
                "jurisdiction_analysis": self._analyze_jurisdiction_content(content, context),
                "cultural_analysis": self._analyze_cultural_content(content, context),
                "legal_analysis": self._analyze_legal_content(content, context),
                "scoring_adjustments": self._calculate_scoring_adjustments(content, context),
                "recommendations": self._generate_jurisdiction_recommendations(content, context)
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Jurisdiction analysis error: {str(e)}")
            raise APIException(
                message="Failed to analyze content with jurisdiction context",
                error_code=APIErrorCodes.EXTERNAL_SERVICE_ERROR,
                status_code=500,
                details={"original_error": str(e)}
            )
    
    def _analyze_jurisdiction_content(self, content: str, context: JurisdictionContext) -> Dict[str, Any]:
        """Analyze content for jurisdiction-specific sensitive topics"""
        country_code = context.country_code
        content_lower = content.lower()
        
        if country_code not in self.sensitive_topics:
            return {"sensitive_topics_found": [], "sensitivity_score": 0.0}
        
        sensitive_topics = self.sensitive_topics[country_code]
        found_topics = []
        total_sensitivity = 0.0
        
        for topic_name, topic_config in sensitive_topics.items():
            found_keywords = []
            sensitivity_score = 0.0
            
            for keyword in topic_config["keywords"]:
                if keyword.lower() in content_lower:
                    found_keywords.append(keyword)
                    sensitivity_score += 1.0
            
            if found_keywords:
                # Adjust sensitivity based on topic config
                topic_sensitivity = topic_config["sensitivity"]
                multiplier = {
                    "very_high": 1.0,
                    "high": 0.7,
                    "moderate": 0.4,
                    "low": 0.2
                }.get(topic_sensitivity, 0.5)
                
                final_sensitivity = (sensitivity_score / len(topic_config["keywords"])) * multiplier
                total_sensitivity += final_sensitivity
                
                found_topics.append({
                    "topic": topic_name,
                    "keywords_found": found_keywords,
                    "sensitivity_level": topic_sensitivity,
                    "sensitivity_score": final_sensitivity,
                    "description": topic_config["description"]
                })
        
        return {
            "sensitive_topics_found": found_topics,
            "total_sensitivity_score": min(total_sensitivity, 1.0),
            "jurisdiction_risk_level": self._assess_jurisdiction_risk(total_sensitivity, context)
        }
    
    def _analyze_cultural_content(self, content: str, context: JurisdictionContext) -> Dict[str, Any]:
        """Analyze content for cultural appropriateness"""
        cultural_context = context.cultural_context
        content_lower = content.lower()
        
        cultural_flags = []
        cultural_score = 0.0
        
        # Check for formality violations
        if cultural_context.get("formality_level") in ["high", "very_high"]:
            informal_indicators = ["hey", "yo", "bro", "dude", "lol", "omg", "wtf"]
            found_informal = [word for word in informal_indicators if word in content_lower]
            if found_informal:
                cultural_flags.append({
                    "issue": "informal_language",
                    "severity": "moderate",
                    "found_words": found_informal,
                    "recommendation": "Use more formal language appropriate for legal content"
                })
                cultural_score += 0.2
        
        # Check for hierarchy violations
        if cultural_context.get("respect_hierarchy") in ["important", "very_important"]:
            disrespectful_terms = ["stupid", "idiot", "moron", "dumb"]
            found_disrespectful = [word for word in disrespectful_terms if word in content_lower]
            if found_disrespectful:
                cultural_flags.append({
                    "issue": "disrespectful_language",
                    "severity": "high",
                    "found_words": found_disrespectful,
                    "recommendation": "Avoid disrespectful language that may violate cultural norms"
                })
                cultural_score += 0.4
        
        # Check for family value violations
        if cultural_context.get("family_values") in ["important", "very_important"]:
            family_offensive = ["bastard", "bitch", "motherfucker"]
            found_family_offensive = [word for word in family_offensive if word in content_lower]
            if found_family_offensive:
                cultural_flags.append({
                    "issue": "family_value_violation",
                    "severity": "high",
                    "found_words": found_family_offensive,
                    "recommendation": "Avoid language that may offend family values"
                })
                cultural_score += 0.3
        
        return {
            "cultural_flags": cultural_flags,
            "cultural_appropriateness_score": max(0.0, 1.0 - cultural_score),
            "cultural_sensitivity_level": cultural_context.get("formality_level", "moderate")
        }
    
    def _analyze_legal_content(self, content: str, context: JurisdictionContext) -> Dict[str, Any]:
        """Analyze content for legal compliance"""
        frameworks = context.legal_frameworks
        country_code = context.country_code
        
        legal_flags = []
        legal_compliance_score = 1.0
        
        # Check for legal framework references
        for framework_name, framework_law in frameworks.items():
            if framework_law.lower() in content.lower():
                legal_flags.append({
                    "type": "legal_framework_reference",
                    "framework": framework_name,
                    "law": framework_law,
                    "status": "appropriate"
                })
        
        # Check for jurisdiction-specific legal terms
        legal_terms = {
            "IN": ["bns", "crpc", "ipc", "constitution", "section", "offence", "punishment"],
            "UK": ["act", "statute", "case law", "precedent", "common law"],
            "US": ["constitution", "amendment", "statute", "code", "precedent"],
            "UAE": ["sharia", "fatwa", "islamic law", "federal law", "emirate law"]
        }
        
        if country_code in legal_terms:
            found_legal_terms = [term for term in legal_terms[country_code] if term in content.lower()]
            if found_legal_terms:
                legal_flags.append({
                    "type": "legal_terminology",
                    "jurisdiction": country_code,
                    "terms_found": found_legal_terms,
                    "status": "appropriate"
                })
                legal_compliance_score += 0.1  # Slight bonus for using correct legal terminology
        
        return {
            "legal_flags": legal_flags,
            "legal_compliance_score": min(legal_compliance_score, 1.0),
            "jurisdiction": country_code,
            "legal_system": context.legal_system
        }
    
    def _calculate_scoring_adjustments(self, content: str, context: JurisdictionContext) -> Dict[str, float]:
        """Calculate jurisdiction-specific scoring adjustments"""
        country_code = context.country_code
        
        if country_code not in self.jurisdiction_rules:
            return {"base_adjustment": 0.0}
        
        rules = self.jurisdiction_rules[country_code]
        adjustments = rules.get("scoring_adjustments", {})
        
        content_lower = content.lower()
        total_adjustment = 0.0
        
        # Calculate adjustments based on found keywords
        for keyword_category, adjustment_value in adjustments.items():
            category_keywords = self._get_category_keywords(keyword_category, country_code)
            found_keywords = sum(1 for keyword in category_keywords if keyword in content_lower)
            
            if found_keywords > 0:
                category_adjustment = adjustment_value * min(found_keywords / len(category_keywords), 1.0)
                total_adjustment += category_adjustment
        
        return {
            "base_adjustment": total_adjustment,
            "jurisdiction_multiplier": self._get_jurisdiction_multiplier(country_code),
            "cultural_adjustment": self._get_cultural_adjustment(content, context)
        }
    
    def _get_category_keywords(self, category: str, country_code: str) -> List[str]:
        """Get keywords for a specific category and jurisdiction"""
        category_mapping = {
            "religious_keywords": ["religious", "god", "allah", "jesus", "buddha", "hindu", "muslim", "christian"],
            "caste_keywords": ["caste", "brahmin", "dalit", "obc", "sc", "st"],
            "political_keywords": ["party", "election", "vote", "government", "politics"],
            "race_keywords": ["race", "racial", "ethnic", "minority"],
            "gun_keywords": ["gun", "weapon", "firearm", "second amendment"],
            "cultural_keywords": ["tradition", "culture", "heritage", "custom"]
        }
        
        return category_mapping.get(category, [])
    
    def _get_jurisdiction_multiplier(self, country_code: str) -> float:
        """Get jurisdiction-specific multiplier"""
        multipliers = {
            "IN": 1.0,
            "UK": 0.9,
            "US": 0.95,
            "UAE": 1.1  # Higher sensitivity
        }
        return multipliers.get(country_code, 1.0)
    
    def _get_cultural_adjustment(self, content: str, context: JurisdictionContext) -> float:
        """Calculate cultural adjustment based on context"""
        cultural_context = context.cultural_context
        
        # Higher sensitivity for formal cultures
        formality_multiplier = {
            "very_high": 0.1,
            "high": 0.05,
            "moderate": 0.0,
            "low": -0.05
        }
        
        return formality_multiplier.get(cultural_context.get("formality_level"), 0.0)
    
    def _assess_jurisdiction_risk(self, sensitivity_score: float, context: JurisdictionContext) -> str:
        """Assess overall jurisdiction risk level"""
        if sensitivity_score >= 0.7:
            return "very_high"
        elif sensitivity_score >= 0.5:
            return "high"
        elif sensitivity_score >= 0.3:
            return "moderate"
        else:
            return "low"
    
    def _generate_jurisdiction_recommendations(
        self, 
        content: str, 
        context: JurisdictionContext
    ) -> List[str]:
        """Generate jurisdiction-specific recommendations"""
        recommendations = []
        
        # Cultural recommendations
        cultural_context = context.cultural_context
        
        if cultural_context.get("formality_level") in ["high", "very_high"]:
            recommendations.append("Consider using more formal language appropriate for legal content")
        
        if cultural_context.get("respect_hierarchy") in ["important", "very_important"]:
            recommendations.append("Avoid language that may disrespect authority or social hierarchy")
        
        if cultural_context.get("religious_sensitivity") in ["high", "very_high"]:
            recommendations.append("Exercise caution with religious references to avoid offense")
        
        # Legal recommendations
        if context.country_code == "IN":
            recommendations.append("Ensure content complies with Indian legal frameworks (BNS, CrPC)")
        elif context.country_code == "UAE":
            recommendations.append("Ensure content respects Islamic values and UAE cultural norms")
        elif context.country_code == "US":
            recommendations.append("Consider First Amendment implications and political sensitivity")
        elif context.country_code == "UK":
            recommendations.append("Ensure content complies with UK defamation and hate speech laws")
        
        return recommendations
    
    def test_multiple_jurisdictions(
        self, 
        content: str, 
        jurisdictions: List[str] = None
    ) -> Dict[str, Any]:
        """Test content across multiple jurisdictions"""
        if jurisdictions is None:
            jurisdictions = ["IN", "UK", "US", "UAE"]
        
        results = {}
        
        for jurisdiction in jurisdictions:
            try:
                analysis = self.analyze_content_jurisdiction(content, jurisdiction)
                results[jurisdiction] = analysis
            except Exception as e:
                logger.error(f"Failed to analyze for jurisdiction {jurisdiction}: {str(e)}")
                results[jurisdiction] = {
                    "error": str(e),
                    "status": "failed"
                }
        
        return {
            "content": content,
            "jurisdictions_tested": jurisdictions,
            "results": results,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }

# Global analyzer instance
jurisdiction_analyzer = JurisdictionAnalyzer()

def analyze_with_jurisdiction(
    content: str, 
    country_code: str = "IN", 
    content_type: str = "text"
) -> Dict[str, Any]:
    """
    Convenience function for jurisdiction-aware content analysis
    """
    return jurisdiction_analyzer.analyze_content_jurisdiction(content, country_code, content_type)

def test_content_jurisdictions(content: str, jurisdictions: List[str] = None) -> Dict[str, Any]:
    """
    Convenience function for testing content across multiple jurisdictions
    """
    return jurisdiction_analyzer.test_multiple_jurisdictions(content, jurisdictions)
#!/usr/bin/env python3
"""
Legal Content Analyzer
======================

Deterministic legal content analysis system to replace random scoring
in BNS/CrPC endpoints. Provides consistent, explainable scoring based on
legal content quality and structure.

Author: Content Moderation System
Version: 1.0.0
"""

import re
import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class LegalContentAnalyzer:
    """
    Advanced legal content analyzer with deterministic scoring
    """
    
    def __init__(self):
        # Legal quality indicators
        self.high_quality_indicators = {
            # Structural elements
            "structural_terms": [
                "shall", "may be", "punished with", "liable to", "whoever", 
                "any person", "court", "magistrate", "section", "act", "law"
            ],
            # Procedural elements
            "procedural_terms": [
                "arrest", "bail", "warrant", "summons", "investigation", 
                "inquiry", "trial", "evidence", "testimony", "witness"
            ],
            # Legal authority terms
            "authority_terms": [
                "government", "police", "officer", "public servant", "judge",
                "high court", "supreme court", "constitution", "legislature"
            ],
            # Punishment and penalty terms
            "punishment_terms": [
                "imprisonment", "fine", "penalty", "punishment", "sentence",
                "detention", "custody", "forfeiture", "confiscation"
            ]
        }
        
        # Quality scoring weights
        self.scoring_weights = {
            "structural_completeness": 0.3,
            "legal_terminology": 0.25,
            "procedural_clarity": 0.2,
            "authority_definition": 0.15,
            "punishment_specification": 0.1
        }
        
        # Red flags that reduce quality score
        self.quality_red_flags = {
            "incomplete_structure": [
                r"\b(?:undefined|unspecified|not mentioned)\b",
                r"\b(?:etc\.?|and so on)\b.*$"
            ],
            "ambiguous_language": [
                r"\b(?:might|could|possibly|perhaps)\b.*\b(?:punish|penalty|liable)\b",
                r"\b(?:subject to|depending on|circumstances)\b.*\b(?:punishment|penalty)\b"
            ],
            "missing_essential_elements": [
                r"(?i)^(?!.*\b(?:shall|may be|whoever|any person)\b).*punish",
                r"(?i)^(?!.*\b(?:court|magistrate|authority)\b).*fine|penalty"
            ]
        }
    
    def analyze_legal_content(
        self, 
        content: str, 
        content_type: str = "legal_text",
        jurisdiction: str = "india"
    ) -> Dict[str, Any]:
        """
        Perform comprehensive legal content analysis
        
        Args:
            content: Legal content text
            content_type: Type of legal content (bns, crpc, etc.)
            jurisdiction: Legal jurisdiction (default: india)
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            content_lower = content.lower()
            word_count = len(content.split())
            
            # Base analysis components
            structural_score = self._analyze_structural_completeness(content_lower)
            terminology_score = self._analyze_legal_terminology(content_lower)
            procedural_score = self._analyze_procedural_clarity(content_lower)
            authority_score = self._analyze_authority_definition(content_lower)
            punishment_score = self._analyze_punishment_specification(content_lower)
            
            # Calculate weighted quality score
            quality_score = (
                structural_score * self.scoring_weights["structural_completeness"] +
                terminology_score * self.scoring_weights["legal_terminology"] +
                procedural_score * self.scoring_weights["procedural_clarity"] +
                authority_score * self.scoring_weights["authority_definition"] +
                punishment_score * self.scoring_weights["punishment_specification"]
            )
            
            # Apply red flag penalties
            red_flag_penalty = self._calculate_red_flag_penalty(content_lower)
            final_quality_score = max(0.0, quality_score - red_flag_penalty)
            
            # Content type specific adjustments
            type_adjusted_score = self._apply_content_type_adjustments(
                final_quality_score, content_type, content_lower
            )
            
            # Jurisdiction specific adjustments
            jurisdiction_adjusted_score = self._apply_jurisdiction_adjustments(
                type_adjusted_score, jurisdiction, content_lower
            )
            
            # Generate detailed analysis
            analysis = {
                "base_quality_score": round(final_quality_score, 3),
                "adjusted_score": round(jurisdiction_adjusted_score, 3),
                "confidence": self._calculate_confidence(content, word_count),
                "content_type": content_type,
                "jurisdiction": jurisdiction,
                "word_count": word_count,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "component_scores": {
                    "structural_completeness": round(structural_score, 3),
                    "legal_terminology": round(terminology_score, 3),
                    "procedural_clarity": round(procedural_score, 3),
                    "authority_definition": round(authority_score, 3),
                    "punishment_specification": round(punishment_score, 3)
                },
                "red_flags": self._identify_red_flags(content_lower),
                "quality_indicators": self._identify_quality_indicators(content_lower),
                "recommendations": self._generate_recommendations(
                    structural_score, terminology_score, procedural_score, 
                    authority_score, punishment_score, red_flag_penalty
                )
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Legal content analysis error: {str(e)}")
            return self._get_fallback_analysis(content)
    
    def _analyze_structural_completeness(self, content: str) -> float:
        """Analyze structural completeness of legal content"""
        score = 0.0
        
        # Check for essential structural elements
        essential_elements = [
            (r"\bwhoever\b", "subject identification"),
            (r"\bshall\b|\bmay be\b", "obligation or possibility"),
            (r"\bpunished with\b|\bliable to\b", "penalty specification"),
            (r"\bsection\b|\bact\b", "legal reference")
        ]
        
        found_elements = 0
        for pattern, description in essential_elements:
            if re.search(pattern, content):
                found_elements += 1
        
        score = (found_elements / len(essential_elements)) * 1.0
        
        # Bonus for complete legal structure
        if re.search(r"\bwhoever.*\bshall.*\bpunished with\b", content, re.DOTALL):
            score += 0.2
        
        return min(score, 1.0)
    
    def _analyze_legal_terminology(self, content: str) -> float:
        """Analyze legal terminology usage"""
        score = 0.0
        
        # Count legal terms from different categories
        total_legal_terms = 0
        for category_terms in self.high_quality_indicators.values():
            for term in category_terms:
                if term in content:
                    total_legal_terms += content.count(term)
        
        # Normalize by content length (assuming average legal content ~100 words)
        normalized_score = min(total_legal_terms / 20.0, 1.0)
        
        # Bonus for diverse legal terminology
        categories_found = 0
        for category in self.high_quality_indicators.keys():
            if any(term in content for term in self.high_quality_indicators[category]):
                categories_found += 1
        
        diversity_bonus = (categories_found / len(self.high_quality_indicators)) * 0.3
        score = normalized_score + diversity_bonus
        
        return min(score, 1.0)
    
    def _analyze_procedural_clarity(self, content: str) -> float:
        """Analyze procedural clarity"""
        score = 0.0
        
        procedural_terms = self.high_quality_indicators["procedural_terms"]
        found_procedural_terms = sum(1 for term in procedural_terms if term in content)
        
        # Score based on procedural term density
        score = min(found_procedural_terms / 5.0, 1.0)
        
        # Check for procedural flow indicators
        flow_indicators = [
            r"\bfirst\b.*\bthen\b",
            r"\bupon\b.*\bshall\b",
            r"\bafter\b.*\bbefore\b"
        ]
        
        flow_bonus = sum(1 for pattern in flow_indicators if re.search(pattern, content)) * 0.1
        score += flow_bonus
        
        return min(score, 1.0)
    
    def _analyze_authority_definition(self, content: str) -> float:
        """Analyze authority and responsibility definition"""
        score = 0.0
        
        authority_terms = self.high_quality_indicators["authority_terms"]
        found_authority_terms = sum(1 for term in authority_terms if term in content)
        
        # Score based on authority term presence
        score = min(found_authority_terms / 4.0, 1.0)
        
        # Check for clear authority hierarchy
        if re.search(r"\b(high court|supreme court).*court\b", content):
            score += 0.2
        
        return min(score, 1.0)
    
    def _analyze_punishment_specification(self, content: str) -> float:
        """Analyze punishment and penalty specification"""
        score = 0.0
        
        punishment_terms = self.high_quality_indicators["punishment_terms"]
        found_punishment_terms = sum(1 for term in punishment_terms if term in content)
        
        # Score based on punishment term specificity
        if "imprisonment" in content and re.search(r"\d+\s*year", content):
            score += 0.4  # Specific imprisonment term
        elif "imprisonment" in content:
            score += 0.2  # General imprisonment
        
        if "fine" in content and re.search(r"₹|\d+", content):
            score += 0.3  # Specific fine amount
        elif "fine" in content:
            score += 0.1  # General fine
        
        # Check for alternative punishments
        if re.search(r"\b(either|or)\b.*\b(imprisonment|fine)\b", content):
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_red_flag_penalty(self, content: str) -> float:
        """Calculate penalty based on red flags"""
        penalty = 0.0
        
        for category, patterns in self.quality_red_flags.items():
            for pattern in patterns:
                if re.search(pattern, content):
                    if category == "incomplete_structure":
                        penalty += 0.3
                    elif category == "ambiguous_language":
                        penalty += 0.2
                    elif category == "missing_essential_elements":
                        penalty += 0.4
        
        return min(penalty, 0.8)  # Cap penalty at 0.8
    
    def _apply_content_type_adjustments(
        self, 
        score: float, 
        content_type: str, 
        content: str
    ) -> float:
        """Apply content type specific adjustments"""
        adjustments = {
            "bns": {
                "penal_code_references": 0.1,
                "bns_specific_terms": 0.1,
                "modern_legal_language": 0.05
            },
            "crpc": {
                "procedure_terms": 0.15,
                "court_procedures": 0.1,
                "legal_processes": 0.1
            },
            "constitution": {
                "constitutional_language": 0.1,
                "fundamental_rights": 0.1,
                "directive_principles": 0.05
            }
        }
        
        if content_type.lower() in adjustments:
            for indicator, bonus in adjustments[content_type.lower()].items():
                if self._check_content_type_indicator(content, indicator):
                    score += bonus
        
        return min(score, 1.0)
    
    def _apply_jurisdiction_adjustments(
        self, 
        score: float, 
        jurisdiction: str, 
        content: str
    ) -> float:
        """Apply jurisdiction specific adjustments"""
        if jurisdiction.lower() == "india":
            # India-specific legal context adjustments
            if re.search(r"\b(IPC|Indian Penal Code|BNS|CrPC)\b", content):
                score += 0.05
            if re.search(r"\b(constitution|fundamental rights)\b", content):
                score += 0.05
        
        return min(score, 1.0)
    
    def _check_content_type_indicator(self, content: str, indicator: str) -> bool:
        """Check for content type specific indicators"""
        indicators_map = {
            "penal_code_references": [r"\b(IPC|penal code|criminal law)\b"],
            "bns_specific_terms": [r"\b(BNS|Bharatiya Nyaya Sanhita)\b"],
            "modern_legal_language": [r"\b(shall|may be|liable to)\b"],
            "procedure_terms": [r"\b(procedure|court|investigation|trial)\b"],
            "court_procedures": [r"\b(warrant|arrest|bail|summons)\b"],
            "legal_processes": [r"\b(evidence|testimony|witness)\b"],
            "constitutional_language": [r"\b(constitution|fundamental|sovereign)\b"],
            "fundamental_rights": [r"\b(right|freedom|equality)\b"],
            "directive_principles": [r"\b(welfare|socialist|secular)\b"]
        }
        
        if indicator in indicators_map:
            for pattern in indicators_map[indicator]:
                if re.search(pattern, content):
                    return True
        
        return False
    
    def _calculate_confidence(self, content: str, word_count: int) -> float:
        """Calculate analysis confidence based on content characteristics"""
        base_confidence = 0.7
        
        # Adjust based on content length
        if word_count < 50:
            base_confidence -= 0.2  # Too short for reliable analysis
        elif word_count > 200:
            base_confidence += 0.1  # Longer content provides more data
        elif word_count > 500:
            base_confidence += 0.15  # Very long content is typically more complete
        
        # Adjust based on legal structure indicators
        structural_indicators = len(re.findall(r"\b(shall|may be|whoever|section|act)\b", content))
        if structural_indicators > 3:
            base_confidence += 0.1
        
        return min(max(base_confidence, 0.3), 0.95)
    
    def _identify_red_flags(self, content: str) -> List[str]:
        """Identify red flags in the content"""
        red_flags = []
        
        for category, patterns in self.quality_red_flags.items():
            for pattern in patterns:
                if re.search(pattern, content):
                    red_flags.append(f"{category.replace('_', ' ').title()}")
        
        return list(set(red_flags))  # Remove duplicates
    
    def _identify_quality_indicators(self, content: str) -> List[str]:
        """Identify positive quality indicators"""
        indicators = []
        
        for category, terms in self.high_quality_indicators.items():
            found_terms = [term for term in terms if term in content]
            if found_terms:
                indicators.append(f"{category.replace('_', ' ').title()}: {', '.join(found_terms[:3])}")
        
        return indicators
    
    def _generate_recommendations(
        self, 
        structural: float, 
        terminology: float, 
        procedural: float,
        authority: float, 
        punishment: float, 
        penalty: float
    ) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        if structural < 0.5:
            recommendations.append("Improve structural completeness with clear subject-verb-object patterns")
        if terminology < 0.5:
            recommendations.append("Enhance legal terminology usage with more precise legal language")
        if procedural < 0.5:
            recommendations.append("Add more procedural clarity with step-by-step legal processes")
        if authority < 0.5:
            recommendations.append("Define authority and responsibility more clearly")
        if punishment < 0.5:
            recommendations.append("Specify punishment and penalties with exact terms and amounts")
        if penalty > 0.3:
            recommendations.append("Remove ambiguous language and incomplete structures")
        
        if not recommendations:
            recommendations.append("Content shows good legal structure and clarity")
        
        return recommendations
    
    def _get_fallback_analysis(self, content: str) -> Dict[str, Any]:
        """Provide fallback analysis when error occurs"""
        word_count = len(content.split())
        return {
            "base_quality_score": 0.5,
            "adjusted_score": 0.5,
            "confidence": 0.3,
            "content_type": "legal_text",
            "jurisdiction": "unknown",
            "word_count": word_count,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "component_scores": {
                "structural_completeness": 0.5,
                "legal_terminology": 0.5,
                "procedural_clarity": 0.5,
                "authority_definition": 0.5,
                "punishment_specification": 0.5
            },
            "red_flags": [],
            "quality_indicators": [],
            "recommendations": ["Analysis error occurred - manual review recommended"],
            "error": "Fallback analysis due to processing error"
        }

# Global instance
legal_analyzer = LegalContentAnalyzer()

def analyze_legal_content(content: str, content_type: str = "legal_text", jurisdiction: str = "india") -> Dict[str, Any]:
    """
    Convenience function for legal content analysis
    """
    return legal_analyzer.analyze_legal_content(content, content_type, jurisdiction)
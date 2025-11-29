"""
NLP-based Content Clarity Analysis Module

This module provides sophisticated text analysis for content clarity assessment,
replacing basic keyword-based approaches with advanced linguistic analysis.
"""

import re
import math
import logging
from typing import Dict, List, Tuple, Any
from collections import Counter
import statistics

logger = logging.getLogger(__name__)

class ContentClarityAnalyzer:
    """
    Advanced content clarity analyzer using NLP techniques
    
    Features:
    - Readability metrics (Flesch Reading Ease, Gunning Fog, etc.)
    - Sentence structure analysis
    - Vocabulary complexity assessment
    - Coherence and logical flow analysis
    - Linguistic pattern recognition
    """
    
    def __init__(self):
        # Common complex words patterns (for readability metrics)
        self.complex_word_patterns = [
            r'\b(?:tion|sion|ment|ness|ity|ism|ing|ed|er|est)\b',  # Common suffixes
            r'\b(?:pre|post|anti|inter|trans|sub|super|ultra|micro|macro)\b',  # Prefixes
        ]
        
        # Legal terminology patterns for legal content analysis
        self.legal_patterns = {
            'complex_legal': [
                r'\b(?:notwithstanding|withstanding|inter alia|pursuant|heretofore|hereinafter|whereas|aforementioned)\b',
                r'\b(?:hitherto|thenceforth|thereinbefore|thereunto|whereby|wherefore|wherein)\b',
                r'\b(?:aforementioned|abovementioned|hereinabove|hereinbefore|thereof|thereat)\b'
            ],
            'simple_legal': [
                r'\b(?:shall|must|may|should|can|court|law|person|crime|penalty|section|act)\b',
                r'\b(?:court|judge|lawyer|legal|rights|duty|offense| punishment| sentence)\b'
            ]
        }
        
        # Clarity issue patterns (more sophisticated than simple keywords)
        self.clarity_indicators = {
            'vague_language': [
                r'\b(?:somewhat|perhaps|maybe|possibly|likely|probably|seems|appears)\b',
                r'\b(?:generally|usually|typically|normally|often|frequently)\b',
                r'\b(?:etc|and so on|and so forth|such as|including)\b'
            ],
            'ambiguous_references': [
                r'\b(?:it|this|that|these|those|such)\b(?!\s+(?:is|are|was|were|shall|will|may|must))',
                r'\b(?:above|below|following|previous|earlier|later)\b(?!\s+(?:section|article|paragraph|clause))',
                r'\b(?:said|such|aforesaid|mentioned)\b(?!\s+(?:person|thing|matter|case))'
            ],
            'complex_sentence_structure': [
                r'[,:;]\s*[,:;]',  # Multiple punctuation marks
                r'\([^)]*\([^)]*',  # Nested parentheses
                r'\b(?:which|that|who|whom|whose)\b.*\b(?:which|that|who|whom|whose)\b',  # Multiple relative clauses
                r'\b(?:although|however|nevertheless|nonetheless|consequently|therefore)\b.*\b(?:although|however|nevertheless|nonetheless|consequently|therefore)\b'  # Multiple conjunctions
            ],
            'incomplete_statements': [
                r'\b(?:etc|and so on|and so forth)\b\.?',  # Incomplete enumerations
                r'["\']\s*$',  # Unclosed quotes
                r'\b(?:as per|as follows|such as|miscellaneous)\b\.?',  # Vague references
            ]
        }
        
        # Positive clarity indicators
        self.clarity_positives = {
            'clear_structure': [
                r'\b(?:first|second|third|finally|initially|therefore|thus|hence)\b',
                r'\b(?:step|phase|stage|process|procedure|method)\b',
                r'\b(?:clearly|definitely|specifically|exactly|precisely)\b'
            ],
            'defined_terms': [
                r'"[^"]+"\s+(?:means|shall mean|is defined as|refers to)',
                r'\b(?:shall be known as|shall be referred to as|is called)\b',
                r'\b(?:definition|defined|meaning|signifies)\b'
            ],
            'logical_flow': [
                r'\b(?:first|secondly|thirdly|finally|in conclusion|to summarize)\b',
                r'\b(?:consequently|therefore|thus|hence|as a result)\b',
                r'\b(?:furthermore|moreover|in addition|additionally)\b'
            ]
        }

    def analyze_content_clarity(self, content: str, content_type: str = "text") -> Dict[str, Any]:
        """
        Comprehensive content clarity analysis
        
        Args:
            content: Text content to analyze
            content_type: Type of content (text, legal, etc.)
            
        Returns:
            Dictionary containing clarity analysis results
        """
        if not content or not content.strip():
            return {
                "clarity_score": 0.0,
                "clarity_issues": ["Empty or whitespace content"],
                "readability_metrics": {},
                "structure_analysis": {},
                "recommendations": ["Provide meaningful content"]
            }
        
        # Perform different types of analysis
        readability_metrics = self._calculate_readability_metrics(content)
        structure_analysis = self._analyze_sentence_structure(content)
        vocabulary_analysis = self._analyze_vocabulary_complexity(content)
        legal_content_analysis = self._analyze_legal_content(content) if content_type == "legal" else {}
        
        # Identify clarity issues
        clarity_issues = self._identify_clarity_issues(content)
        
        # Calculate overall clarity score
        clarity_score = self._calculate_clarity_score(
            readability_metrics, structure_analysis, vocabulary_analysis, 
            legal_content_analysis, clarity_issues
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            readability_metrics, structure_analysis, vocabulary_analysis, 
            clarity_issues, content_type
        )
        
        return {
            "clarity_score": round(clarity_score, 3),
            "clarity_issues": clarity_issues,
            "readability_metrics": readability_metrics,
            "structure_analysis": structure_analysis,
            "vocabulary_analysis": vocabulary_analysis,
            "legal_content_analysis": legal_content_analysis,
            "recommendations": recommendations,
            "content_type": content_type,
            "analysis_timestamp": self._get_timestamp()
        }

    def _calculate_readability_metrics(self, content: str) -> Dict[str, float]:
        """Calculate various readability metrics"""
        # Basic text statistics
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        words = re.findall(r'\b\w+\b', content.lower())
        syllables = sum(self._count_syllables(word) for word in words)
        
        if not sentences or not words:
            return {"error": "Insufficient content for readability analysis"}
        
        # Average words per sentence
        avg_words_per_sentence = len(words) / len(sentences)
        
        # Average syllables per word
        avg_syllables_per_word = syllables / len(words) if words else 0
        
        # Flesch Reading Ease Score
        # Formula: 206.835 - 1.015 * (avg_words_per_sentence) - 84.6 * (avg_syllables_per_word)
        flesch_score = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
        flesch_score = max(0, min(100, flesch_score))  # Clamp between 0-100
        
        # Flesch-Kincaid Grade Level
        fk_grade = (0.39 * avg_words_per_sentence) + (11.8 * avg_syllables_per_word) - 15.59
        
        # Gunning Fog Index
        complex_words = sum(1 for word in words if self._is_complex_word(word))
        complex_word_ratio = complex_words / len(words) if words else 0
        gunning_fog = 0.4 * (avg_words_per_sentence + (100 * complex_word_ratio))
        
        # Coleman-Liau Index
        letters = sum(len(word) for word in words)
        chars = len(re.sub(r'[^a-zA-Z]', '', content))
        L = (letters / len(words)) * 100 if words else 0
        S = (len(sentences) / len(words)) * 100 if words else 0
        coleman_liau = 0.0588 * L - 0.296 * S - 15.8
        
        # Automated Readability Index
        chars_per_word = chars / len(words) if words else 0
        ari = 4.71 * chars_per_word + 0.5 * avg_words_per_sentence - 21.43
        
        return {
            "flesch_reading_ease": round(flesch_score, 2),
            "flesch_kincaid_grade": round(fk_grade, 2),
            "gunning_fog_index": round(gunning_fog, 2),
            "coleman_liau_index": round(coleman_liau, 2),
            "automated_readability_index": round(ari, 2),
            "avg_words_per_sentence": round(avg_words_per_sentence, 2),
            "avg_syllables_per_word": round(avg_syllables_per_word, 2),
            "complex_word_ratio": round(complex_word_ratio, 3),
            "total_sentences": len(sentences),
            "total_words": len(words),
            "total_syllables": syllables
        }

    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word"""
        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Handle silent 'e'
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
            
        # Ensure at least 1 syllable
        return max(1, syllable_count)

    def _is_complex_word(self, word: str) -> bool:
        """Determine if a word is complex (3+ syllables)"""
        return self._count_syllables(word) >= 3

    def _analyze_sentence_structure(self, content: str) -> Dict[str, Any]:
        """Analyze sentence structure and complexity"""
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return {"error": "No sentences found"}
        
        # Analyze each sentence
        sentence_metrics = []
        for sentence in sentences:
            words = re.findall(r'\b\w+\b', sentence)
            clauses = len(re.findall(r'[,;:]', sentence)) + 1  # Approximate clause count
            
            sentence_metrics.append({
                "word_count": len(words),
                "clause_count": clauses,
                "avg_word_length": sum(len(w) for w in words) / len(words) if words else 0,
                "contains_question": '?' in sentence,
                "contains_exclamation": '!' in sentence,
                "has_relative_clauses": bool(re.search(r'\b(which|that|who|whom|whose)\b', sentence, re.IGNORECASE)),
                "has_coordinating_conjunctions": bool(re.search(r'\b(and|or|but|nor|for|so|yet)\b', sentence, re.IGNORECASE)),
                "has_subordinating_conjunctions": bool(re.search(r'\b(because|although|since|unless|while|whereas)\b', sentence, re.IGNORECASE))
            })
        
        # Calculate aggregate metrics
        word_counts = [m["word_count"] for m in sentence_metrics]
        clause_counts = [m["clause_count"] for m in sentence_metrics]
        
        return {
            "total_sentences": len(sentences),
            "avg_sentence_length": round(statistics.mean(word_counts), 2),
            "median_sentence_length": round(statistics.median(word_counts), 2),
            "max_sentence_length": max(word_counts),
            "min_sentence_length": min(word_counts),
            "avg_clauses_per_sentence": round(statistics.mean(clause_counts), 2),
            "sentence_length_variance": round(statistics.variance(word_counts), 2) if len(word_counts) > 1 else 0,
            "short_sentences": sum(1 for wc in word_counts if wc < 10),
            "medium_sentences": sum(1 for wc in word_counts if 10 <= wc <= 20),
            "long_sentences": sum(1 for wc in word_counts if wc > 20),
            "questions": sum(1 for m in sentence_metrics if m["contains_question"]),
            "exclamations": sum(1 for m in sentence_metrics if m["contains_exclamation"]),
            "complex_structures": sum(1 for m in sentence_metrics if m["has_relative_clauses"] or m["has_subordinating_conjunctions"]),
            "sentence_details": sentence_metrics[:5]  # First 5 sentences for detailed analysis
        }

    def _analyze_vocabulary_complexity(self, content: str) -> Dict[str, Any]:
        """Analyze vocabulary complexity and diversity"""
        words = re.findall(r'\b\w+\b', content.lower())
        
        if not words:
            return {"error": "No words found"}
        
        # Word frequency analysis
        word_freq = Counter(words)
        total_words = len(words)
        unique_words = len(word_freq)
        
        # Type-Token Ratio (lexical diversity)
        ttr = unique_words / total_words
        
        # Hapax legomena (words that appear only once)
        hapax_count = sum(1 for count in word_freq.values() if count == 1)
        hapax_ratio = hapax_count / unique_words if unique_words > 0 else 0
        
        # Average word length
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Word length distribution
        word_lengths = [len(word) for word in words]
        short_words = sum(1 for wl in word_lengths if wl <= 4)
        medium_words = sum(1 for wl in word_lengths if 5 <= wl <= 8)
        long_words = sum(1 for wl in word_lengths if wl >= 9)
        
        # Syllable complexity
        syllable_counts = [self._count_syllables(word) for word in words]
        avg_syllables = statistics.mean(syllable_counts)
        complex_words = sum(1 for sc in syllable_counts if sc >= 3)
        
        # Most frequent words (excluding common stop words)
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an'}
        frequent_words = [(word, count) for word, count in word_freq.most_common(10) 
                         if word not in stop_words]
        
        return {
            "total_words": total_words,
            "unique_words": unique_words,
            "type_token_ratio": round(ttr, 3),
            "hapax_legomena": hapax_count,
            "hapax_ratio": round(hapax_ratio, 3),
            "avg_word_length": round(avg_word_length, 2),
            "word_length_distribution": {
                "short_words": short_words,
                "medium_words": medium_words,
                "long_words": long_words
            },
            "syllable_analysis": {
                "avg_syllables": round(avg_syllables, 2),
                "complex_words": complex_words,
                "complex_word_ratio": round(complex_words / total_words, 3)
            },
            "vocabulary_richness": "high" if ttr > 0.5 else "medium" if ttr > 0.3 else "low",
            "most_frequent_words": frequent_words[:5]
        }

    def _analyze_legal_content(self, content: str) -> Dict[str, Any]:
        """Specialized analysis for legal content"""
        content_lower = content.lower()
        
        # Count legal terminology
        complex_legal_count = sum(len(re.findall(pattern, content_lower)) 
                                 for pattern in self.legal_patterns['complex_legal'])
        simple_legal_count = sum(len(re.findall(pattern, content_lower)) 
                               for pattern in self.legal_patterns['simple_legal'])
        
        # Legal structure indicators
        has_sections = bool(re.search(r'\b(?:section|article|clause|paragraph)\b', content_lower))
        has_definitions = bool(re.search(r'\b(?:shall mean|is defined as|means)\b', content_lower))
        has_citations = bool(re.search(r'\b(?:\d+\.\d+|\([a-z]\)|section\s+\d+)\b', content_lower))
        
        # Legal language complexity
        total_legal_terms = complex_legal_count + simple_legal_count
        legal_term_density = total_legal_terms / len(content.split()) if content.split() else 0
        
        return {
            "complex_legal_terms": complex_legal_count,
            "simple_legal_terms": simple_legal_count,
            "legal_term_density": round(legal_term_density, 4),
            "has_structured_format": has_sections,
            "has_definitions": has_definitions,
            "has_citations": has_citations,
            "legal_language_complexity": "high" if complex_legal_count > simple_legal_count else "balanced",
            "recommendations": self._generate_legal_recommendations(complex_legal_count, simple_legal_count, has_definitions)
        }

    def _identify_clarity_issues(self, content: str) -> List[str]:
        """Identify specific clarity issues using advanced pattern matching"""
        issues = []
        content_lower = content.lower()
        
        # Check each category of clarity issues
        for category, patterns in self.clarity_indicators.items():
            matches = []
            for pattern in patterns:
                found_matches = re.findall(pattern, content_lower)
                if found_matches:
                    matches.extend(found_matches)
            
            if matches:
                issue_count = len(matches)
                if issue_count > 0:
                    if category == 'vague_language':
                        issues.append(f"Vague language detected ({issue_count} instances): use more specific terminology")
                    elif category == 'ambiguous_references':
                        issues.append(f"Ambiguous references found ({issue_count} instances): clarify pronoun and reference usage")
                    elif category == 'complex_sentence_structure':
                        issues.append(f"Overly complex sentence structures ({issue_count} instances): break down long sentences")
                    elif category == 'incomplete_statements':
                        issues.append(f"Incomplete or vague statements ({issue_count} instances): provide complete information")
        
        # Check for structural issues
        if len(content.split('.')) < 2:
            issues.append("Content lacks proper sentence structure or is very brief")
        
        # Check for excessive repetition
        words = content.lower().split()
        word_freq = Counter(words)
        if word_freq:
            most_common = word_freq.most_common(1)[0]
            if most_common[1] > len(words) * 0.1:  # Word appears more than 10% of time
                issues.append(f"Excessive repetition of word '{most_common[0]}' may reduce clarity")
        
        # Check for very long paragraphs (poor structure)
        paragraphs = content.split('\n\n')
        long_paragraphs = sum(1 for p in paragraphs if len(p.split()) > 200)
        if long_paragraphs > 0:
            issues.append(f"Very long paragraphs detected ({long_paragraphs}): consider breaking into smaller sections")
        
        return issues

    def _calculate_clarity_score(self, readability: Dict, structure: Dict, 
                               vocabulary: Dict, legal: Dict, issues: List[str]) -> float:
        """Calculate overall clarity score (0-1, higher is better)"""
        score = 1.0
        
        # Deduct points for clarity issues
        score -= len(issues) * 0.1
        
        # Readability score (higher Flesch score = better readability)
        if 'flesch_reading_ease' in readability:
            flesch = readability['flesch_reading_ease']
            if flesch >= 70:  # Easy to read
                score += 0.1
            elif flesch >= 50:  # Moderately easy
                score += 0.05
            elif flesch < 30:  # Very difficult
                score -= 0.1
        
        # Structure score
        if 'avg_sentence_length' in structure:
            avg_length = structure['avg_sentence_length']
            if 10 <= avg_length <= 20:  # Optimal range
                score += 0.1
            elif avg_length > 30:  # Too long
                score -= 0.1
            elif avg_length < 5:  # Too short
                score -= 0.05
        
        # Vocabulary diversity score
        if 'type_token_ratio' in vocabulary:
            ttr = vocabulary['type_token_ratio']
            if ttr > 0.5:  # Good vocabulary diversity
                score += 0.05
            elif ttr < 0.3:  # Poor vocabulary diversity
                score -= 0.05
        
        # Legal content specific adjustments
        if legal and 'legal_term_density' in legal:
            density = legal['legal_term_density']
            if 0.02 <= density <= 0.05:  # Good legal term density
                score += 0.05
            elif density > 0.1:  # Too dense
                score -= 0.05
        
        return max(0.0, min(1.0, score))

    def _generate_recommendations(self, readability: Dict, structure: Dict, 
                                vocabulary: Dict, issues: List[str], content_type: str) -> List[str]:
        """Generate specific recommendations for improving content clarity"""
        recommendations = []
        
        # Recommendations based on readability metrics
        if 'flesch_reading_ease' in readability:
            flesch = readability['flesch_reading_ease']
            if flesch < 50:
                recommendations.append("Consider using shorter sentences and simpler words to improve readability")
            if flesch > 80 and content_type == "legal":
                recommendations.append("Consider adding more precise legal terminology for accuracy")
        
        # Recommendations based on sentence structure
        if 'avg_sentence_length' in structure:
            avg_length = structure['avg_sentence_length']
            if avg_length > 25:
                recommendations.append("Break down long sentences into shorter, clearer statements")
            if structure.get('long_sentences', 0) > structure.get('short_sentences', 0):
                recommendations.append("Use more short sentences for better readability")
        
        # Recommendations based on vocabulary
        if 'type_token_ratio' in vocabulary and vocabulary['type_token_ratio'] < 0.3:
            recommendations.append("Increase vocabulary diversity by varying word choice")
        
        # Recommendations based on identified issues
        for issue in issues:
            if "vague language" in issue:
                recommendations.append("Replace vague terms with specific, concrete language")
            elif "ambiguous references" in issue:
                recommendations.append("Replace pronouns with specific nouns or provide clear antecedents")
            elif "complex sentence structure" in issue:
                recommendations.append("Simplify sentence structure and reduce subordinate clauses")
            elif "incomplete statements" in issue:
                recommendations.append("Complete all statements and avoid vague references")
        
        # Content-type specific recommendations
        if content_type == "legal":
            if not any('definition' in rec.lower() for rec in recommendations):
                recommendations.append("Ensure key legal terms are clearly defined")
            recommendations.append("Use consistent legal terminology throughout")
        
        return recommendations[:5]  # Return top 5 recommendations

    def _generate_legal_recommendations(self, complex_count: int, simple_count: int, 
                                      has_definitions: bool) -> List[str]:
        """Generate recommendations for legal content"""
        recommendations = []
        
        if complex_count > simple_count * 2:
            recommendations.append("Consider simplifying complex legal terminology for clarity")
        
        if not has_definitions:
            recommendations.append("Add clear definitions for key legal terms")
        
        if complex_count == 0:
            recommendations.append("Consider adding appropriate legal terminology for precision")
        
        return recommendations

    def _get_timestamp(self) -> str:
        """Get current timestamp for analysis"""
        from datetime import datetime
        return datetime.utcnow().isoformat()


def create_clarity_analyzer() -> ContentClarityAnalyzer:
    """Factory function to create clarity analyzer instance"""
    return ContentClarityAnalyzer()


def analyze_content_clarity(content: str, content_type: str = "text") -> Dict[str, Any]:
    """
    Convenience function for content clarity analysis
    
    Args:
        content: Text content to analyze
        content_type: Type of content (text, legal, etc.)
        
    Returns:
        Dictionary containing clarity analysis results
    """
    analyzer = create_clarity_analyzer()
    return analyzer.analyze_content_clarity(content, content_type)
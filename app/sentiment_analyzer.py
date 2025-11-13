#!/usr/bin/env python3
"""
Sentiment analysis for content moderation feedback and analytics
"""

import re
from typing import Tuple, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

# Try to import vaderSentiment, fallback to simple analysis
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False

class SentimentAnalyzer:
    """Advanced sentiment analysis for content moderation"""

    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer() if VADER_AVAILABLE else None

        # Extended word lists for content moderation context
        self.positive_words = {
            'good', 'great', 'excellent', 'amazing', 'awesome', 'love', 'like',
            'fantastic', 'wonderful', 'perfect', 'best', 'brilliant', 'outstanding',
            'helpful', 'useful', 'accurate', 'appropriate', 'safe', 'clean',
            'appropriate', 'suitable', 'acceptable', 'reasonable', 'fair'
        }

        self.negative_words = {
            'bad', 'terrible', 'awful', 'hate', 'dislike', 'worst', 'horrible',
            'poor', 'disappointing', 'boring', 'slow', 'confusing', 'annoying',
            'inappropriate', 'offensive', 'harmful', 'dangerous', 'toxic', 'abusive',
            'spam', 'scam', 'fraud', 'misleading', 'false', 'incorrect'
        }

        # Legal and content-specific terms
        self.legal_positive = {
            'constitutional', 'legal', 'lawful', 'compliant', 'valid', 'legitimate',
            'authorized', 'permitted', 'allowed', 'approved'
        }

        self.legal_negative = {
            'unconstitutional', 'illegal', 'unlawful', 'non-compliant', 'invalid',
            'illegitimate', 'unauthorized', 'prohibited', 'banned', 'forbidden'
        }

        logger.info(f"SentimentAnalyzer initialized with VADER: {VADER_AVAILABLE}")

    def analyze_sentiment(self, text: str, rating: int = None, context: str = "general") -> Dict[str, Any]:
        """
        Analyze sentiment from text and rating with context awareness
        Returns comprehensive sentiment analysis
        """
        if not text:
            text = ""

        # Use VADER if available, otherwise fallback to simple analysis
        if self.vader_analyzer and text.strip():
            base_sentiment = self._analyze_with_vader(text, rating)
        else:
            base_sentiment = self._analyze_simple(text, rating)

        # Context-specific adjustments
        adjusted_sentiment = self._apply_context_adjustments(base_sentiment, text, context)

        # Calculate engagement and other metrics
        engagement_score = self._calculate_engagement(text, rating)
        toxicity_score = self._calculate_toxicity(text)
        confidence_score = self._calculate_confidence(text, rating)

        return {
            "sentiment": adjusted_sentiment["label"],
            "polarity_score": adjusted_sentiment["score"],
            "confidence": confidence_score,
            "engagement_score": engagement_score,
            "toxicity_score": toxicity_score,
            "context": context,
            "word_count": len(text.split()) if text else 0,
            "has_rating": rating is not None,
            "rating": rating,
            "analysis_method": "vader" if self.vader_analyzer else "simple"
        }

    def _analyze_with_vader(self, text: str, rating: int = None) -> Dict[str, Any]:
        """Analyze sentiment using VADER"""
        scores = self.vader_analyzer.polarity_scores(text)
        compound = scores['compound']

        # Combine VADER score with rating if available
        if rating:
            # Convert 1-5 rating to -1 to 1 scale
            rating_sentiment = (rating - 3) / 2.0
            # Weight VADER 70%, rating 30%
            combined_score = (compound * 0.7) + (rating_sentiment * 0.3)
        else:
            combined_score = compound

        # Determine label
        if combined_score >= 0.1:
            label = "positive"
        elif combined_score <= -0.1:
            label = "negative"
        else:
            label = "neutral"

        return {
            "label": label,
            "score": round(combined_score, 3),
            "vader_scores": scores
        }

    def _analyze_simple(self, text: str, rating: int = None) -> Dict[str, Any]:
        """Simple sentiment analysis fallback"""
        # Clean and tokenize text
        words = re.findall(r'\b\w+\b', text.lower()) if text else []

        # Count sentiment words
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)

        # Legal context words
        legal_pos_count = sum(1 for word in words if word in self.legal_positive)
        legal_neg_count = sum(1 for word in words if word in self.legal_negative)

        # Determine sentiment based on rating and text
        if rating:
            if rating >= 4:
                label = "positive"
                score = 0.5 + (rating - 4) * 0.25  # 0.5 to 0.75
            elif rating <= 2:
                label = "negative"
                score = -0.5 + (2 - rating) * 0.25  # -0.5 to -0.75
            else:
                label = "neutral"
                score = 0.0
        else:
            # Use text analysis
            total_sentiment = positive_count - negative_count
            legal_sentiment = legal_pos_count - legal_neg_count

            # Weight legal terms higher
            combined_sentiment = total_sentiment + (legal_sentiment * 1.5)

            if combined_sentiment > 0:
                label = "positive"
                score = min(combined_sentiment * 0.1, 0.8)
            elif combined_sentiment < 0:
                label = "negative"
                score = max(combined_sentiment * 0.1, -0.8)
            else:
                label = "neutral"
                score = 0.0

        return {
            "label": label,
            "score": round(score, 3)
        }

    def _apply_context_adjustments(self, base_sentiment: Dict[str, Any], text: str, context: str) -> Dict[str, Any]:
        """Apply context-specific sentiment adjustments"""
        adjusted = base_sentiment.copy()

        if context == "legal":
            # In legal context, certain terms have stronger weight
            legal_terms = ['constitutional', 'illegal', 'unlawful', 'compliant', 'violation']
            has_legal_terms = any(term in text.lower() for term in legal_terms)

            if has_legal_terms:
                # Increase magnitude of sentiment for legal discussions
                adjusted["score"] = adjusted["score"] * 1.2

        elif context == "moderation_feedback":
            # In moderation feedback, look for specific improvement suggestions
            improvement_terms = ['should', 'could', 'would', 'better', 'improve', 'suggest']
            has_improvement = any(term in text.lower() for term in improvement_terms)

            if has_improvement and adjusted["label"] == "negative":
                # Constructive criticism might be more neutral
                adjusted["score"] = adjusted["score"] * 0.7

        return adjusted

    def _calculate_engagement(self, text: str, rating: int = None) -> float:
        """Calculate engagement score (0-1)"""
        if not text:
            base_engagement = 0.0
        else:
            # Text length component (longer comments = higher engagement)
            text_length_score = min(len(text) / 100, 1.0)

            # Word count component (more words = higher engagement)
            word_count = len(text.split())
            word_score = min(word_count / 20, 1.0)  # Cap at 20 words

            base_engagement = (text_length_score * 0.5) + (word_score * 0.5)

        # Rating component
        if rating:
            # Extreme ratings show higher engagement
            rating_engagement = 1.0 if rating in [1, 2, 5] else 0.6
            base_engagement = (base_engagement * 0.7) + (rating_engagement * 0.3)

        return round(base_engagement, 3)

    def _calculate_toxicity(self, text: str) -> float:
        """Calculate toxicity score (0-1)"""
        if not text:
            return 0.0

        words = re.findall(r'\b\w+\b', text.lower())
        total_words = len(words)

        if total_words == 0:
            return 0.0

        # Count toxic words
        toxic_words = ['hate', 'stupid', 'idiot', 'dumb', 'suck', 'crap', 'shit', 'fuck']
        toxic_count = sum(1 for word in words if word in toxic_words)

        # Check for repeated punctuation (anger indicator)
        anger_indicators = len(re.findall(r'[!]{2,}', text)) + len(re.findall(r'[?]{2,}', text))

        # Calculate toxicity score
        word_toxicity = toxic_count / total_words
        anger_toxicity = min(anger_indicators * 0.1, 0.5)  # Cap at 0.5

        toxicity_score = (word_toxicity * 0.7) + (anger_toxicity * 0.3)

        return round(min(toxicity_score, 1.0), 3)

    def _calculate_confidence(self, text: str, rating: int = None) -> float:
        """Calculate confidence in sentiment analysis (0-1)"""
        confidence_factors = []

        # Text length confidence
        if text:
            length_confidence = min(len(text) / 50, 1.0)  # Longer text = higher confidence
            confidence_factors.append(length_confidence)
        else:
            confidence_factors.append(0.0)

        # Rating confidence
        if rating is not None:
            rating_confidence = 1.0  # Explicit rating = high confidence
            confidence_factors.append(rating_confidence)
        else:
            confidence_factors.append(0.5)  # No rating = medium confidence

        # Analysis method confidence
        method_confidence = 1.0 if self.vader_analyzer else 0.7
        confidence_factors.append(method_confidence)

        # Average confidence
        avg_confidence = sum(confidence_factors) / len(confidence_factors)

        return round(avg_confidence, 3)

    def analyze_batch(self, texts: List[str], ratings: List[int] = None, context: str = "general") -> List[Dict[str, Any]]:
        """Analyze sentiment for multiple texts"""
        if ratings and len(ratings) != len(texts):
            raise ValueError("Ratings list must match texts list length")

        results = []
        for i, text in enumerate(texts):
            rating = ratings[i] if ratings else None
            result = self.analyze_sentiment(text, rating, context)
            results.append(result)

        return results

    def get_sentiment_summary(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics from sentiment analyses"""
        if not analyses:
            return {}

        total_count = len(analyses)

        # Count sentiments
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        for analysis in analyses:
            sentiment = analysis.get("sentiment", "neutral")
            sentiment_counts[sentiment] += 1

        # Calculate averages
        avg_polarity = sum(a.get("polarity_score", 0) for a in analyses) / total_count
        avg_engagement = sum(a.get("engagement_score", 0) for a in analyses) / total_count
        avg_toxicity = sum(a.get("toxicity_score", 0) for a in analyses) / total_count
        avg_confidence = sum(a.get("confidence", 0) for a in analyses) / total_count

        return {
            "total_analyses": total_count,
            "sentiment_distribution": {
                sentiment: {
                    "count": count,
                    "percentage": round((count / total_count) * 100, 1)
                }
                for sentiment, count in sentiment_counts.items()
            },
            "average_scores": {
                "polarity": round(avg_polarity, 3),
                "engagement": round(avg_engagement, 3),
                "toxicity": round(avg_toxicity, 3),
                "confidence": round(avg_confidence, 3)
            },
            "dominant_sentiment": max(sentiment_counts, key=sentiment_counts.get)
        }

# Global analyzer instance
sentiment_analyzer = SentimentAnalyzer()
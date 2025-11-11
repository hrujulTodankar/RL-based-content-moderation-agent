#!/usr/bin/env python3
"""
Flagged Words Database for Content Moderation
=============================================

Comprehensive database of words and phrases that should be flagged
during content moderation, organized by categories and severity levels.

This file serves as the central repository for all flagged content
used by the RL-powered moderation system.

Author: Content Moderation System
Version: 1.0.0
"""

from typing import Dict, List, Set, Tuple
import re


class FlaggedWordsDatabase:
    """Database containing all flagged words and phrases for content moderation"""

    def __init__(self):
        """Initialize the flagged words database"""
        self.criminal_offenses = self._get_criminal_offenses()
        self.hate_speech = self._get_hate_speech()
        self.violence = self._get_violence_words()
        self.harassment = self._get_harassment_words()
        self.profanity = self._get_profanity()
        self.spam_indicators = self._get_spam_indicators()
        self.illegal_activities = self._get_illegal_activities()

        # Combine all categories
        self.all_flagged_words = self._combine_all_categories()

        # Severity weights
        self.severity_weights = {
            'critical': 1.0,    # Immediate flagging (score >= 0.8)
            'high': 0.7,        # High priority flagging (score >= 0.6)
            'medium': 0.4,      # Medium priority flagging (score >= 0.4)
            'low': 0.2          # Low priority flagging (score >= 0.2)
        }

    def _get_criminal_offenses(self) -> Dict[str, str]:
        """Criminal offenses from BNS 2023 and IPC"""
        return {
            # Murder and homicide
            'murder': 'critical', 'kill': 'critical', 'homicide': 'critical',
            'manslaughter': 'high', 'assassinate': 'critical', 'slaughter': 'critical',

            # Sexual offenses
            'rape': 'critical', 'molest': 'critical', 'molestation': 'critical',
            'sexual assault': 'critical', 'incest': 'critical', 'sodomy': 'high',

            # Violence and assault
            'assault': 'high', 'attack': 'high', 'beat': 'high', 'batter': 'high',
            'abuse': 'high', 'torture': 'critical', 'mutilate': 'critical',

            # Theft and robbery
            'theft': 'high', 'robbery': 'high', 'burglary': 'high', 'steal': 'high',
            'loot': 'high', 'plunder': 'high', 'dacoity': 'critical',

            # Fraud and cheating
            'fraud': 'high', 'cheat': 'high', 'scam': 'high', 'deceive': 'medium',
            'forgery': 'high', 'counterfeit': 'high', 'fake': 'medium',

            # Drugs and narcotics
            'drugs': 'high', 'narcotics': 'high', 'heroin': 'critical',
            'cocaine': 'critical', 'meth': 'critical', 'opium': 'high',

            # Terrorism and organized crime
            'terrorism': 'critical', 'terrorist': 'critical', 'bomb': 'critical',
            'explosive': 'critical', 'organized crime': 'critical', 'mafia': 'high',

            # Other serious crimes
            'kidnapping': 'critical', 'abduction': 'critical', 'extortion': 'high',
            'blackmail': 'high', 'defamation': 'medium', 'slander': 'medium'
        }

    def _get_hate_speech(self) -> Dict[str, str]:
        """Hate speech and discriminatory terms"""
        return {
            # Racial/ethnic slurs
            'racist': 'critical', 'nigger': 'critical', 'chink': 'critical',
            'gook': 'critical', 'spic': 'critical', 'wetback': 'critical',

            # Religious discrimination
            'islamophobe': 'high', 'christianophobe': 'high', 'hinduphobe': 'high',
            'antisemite': 'high', 'blasphemy': 'high',

            # Gender discrimination
            'misogynist': 'high', 'sexist': 'high', 'homophobe': 'high',
            'transphobe': 'high', 'patriarchy': 'medium',

            # General hate terms
            'hate': 'high', 'discrimination': 'medium', 'prejudice': 'medium',
            'bigotry': 'high', 'intolerance': 'medium'
        }

    def _get_violence_words(self) -> Dict[str, str]:
        """Violence-related words and phrases"""
        return {
            'violent': 'high', 'violence': 'high', 'brutal': 'high',
            'savage': 'high', 'barbaric': 'high', 'cruel': 'high',
            'merciless': 'high', 'ruthless': 'high', 'vicious': 'high',
            'aggressive': 'medium', 'hostile': 'medium', 'threatening': 'high',
            'intimidate': 'high', 'menace': 'high', 'coerce': 'medium',
            # Borderline words that should NOT be flagged
            'harmless': 'none', 'innocent': 'none', 'peaceful': 'none',
            'gentle': 'none', 'kind': 'none', 'benevolent': 'none',
            'safe': 'none', 'secure': 'none', 'protected': 'none',
            'defensive': 'none', 'self-defense': 'none', 'protection': 'none'
        }

    def _get_harassment_words(self) -> Dict[str, str]:
        """Harassment and stalking related terms"""
        return {
            'harassment': 'high', 'harass': 'high', 'stalk': 'high',
            'stalking': 'high', 'bully': 'high', 'bullying': 'high',
            'intimidation': 'high', 'threat': 'high', 'menace': 'high',
            'persecute': 'high', 'torment': 'high', 'annoy': 'medium'
        }

    def _get_profanity(self) -> Dict[str, str]:
        """Profanity and vulgar language"""
        return {
            # Strong profanity
            'fuck': 'high', 'shit': 'medium', 'damn': 'low', 'hell': 'low',
            'asshole': 'high', 'bastard': 'high', 'bitch': 'high',
            'cunt': 'critical', 'motherfucker': 'critical',

            # Mild profanity
            'dumb': 'low', 'stupid': 'low', 'idiot': 'medium',
            'moron': 'medium', 'jerk': 'medium'
        }

    def _get_spam_indicators(self) -> Dict[str, str]:
        """Spam and promotional content indicators"""
        return {
            'spam': 'high', 'scam': 'high', 'fraud': 'high',
            'fake': 'medium', 'bogus': 'medium', 'phishing': 'high',
            'malware': 'high', 'virus': 'high', 'hack': 'medium',
            'crack': 'medium', 'pirate': 'medium', 'torrent': 'medium',
            'advertisement': 'medium', 'promo': 'medium', 'marketing': 'low',
            'click here': 'medium', 'buy now': 'medium', 'limited time': 'medium',
            'free gift': 'medium', 'win prize': 'medium', 'lottery': 'high',
            'casino': 'high', 'gambling': 'high', 'betting': 'high'
        }

    def _get_illegal_activities(self) -> Dict[str, str]:
        """Illegal activities and prohibited content"""
        return {
            'illegal': 'high', 'prohibited': 'high', 'banned': 'high',
            'contraband': 'high', 'smuggle': 'high', 'traffick': 'critical',
            'corrupt': 'high', 'bribery': 'high', 'embezzle': 'high',
            'launder': 'high', 'evade': 'high', 'tax evasion': 'high'
        }

    def _combine_all_categories(self) -> Dict[str, str]:
        """Combine all categories into a single dictionary"""
        combined = {}
        combined.update(self.criminal_offenses)
        combined.update(self.hate_speech)
        combined.update(self.violence)
        combined.update(self.harassment)
        combined.update(self.profanity)
        combined.update(self.spam_indicators)
        combined.update(self.illegal_activities)

        # Filter out 'none' severity words (words that should not be flagged)
        filtered_combined = {word: severity for word, severity in combined.items() if severity != 'none'}
        return filtered_combined

    def get_flagged_words_by_category(self, category: str) -> Dict[str, str]:
        """Get flagged words for a specific category"""
        category_map = {
            'criminal': self.criminal_offenses,
            'hate': self.hate_speech,
            'violence': self.violence,
            'harassment': self.harassment,
            'profanity': self.profanity,
            'spam': self.spam_indicators,
            'illegal': self.illegal_activities,
            'all': self.all_flagged_words
        }
        return category_map.get(category.lower(), {})

    def check_content(self, content: str, category: str = 'all') -> Tuple[List[str], float]:
        """
        Check content against flagged words

        Returns:
            Tuple of (matched_words, total_score)
        """
        content_lower = content.lower()
        flagged_words = self.get_flagged_words_by_category(category)

        matched_words = []
        total_score = 0.0

        for word, severity in flagged_words.items():
            if word in content_lower:
                # Skip words marked as 'none' (should not be flagged)
                if severity == 'none':
                    continue
                matched_words.append(word)
                total_score += self.severity_weights.get(severity, 0.0)

        return matched_words, min(total_score, 2.0)  # Cap at 2.0

    def get_critical_words(self) -> List[str]:
        """Get all critical severity words"""
        return [word for word, severity in self.all_flagged_words.items()
                if severity == 'critical']

    def get_high_priority_words(self) -> List[str]:
        """Get all high severity words"""
        return [word for word, severity in self.all_flagged_words.items()
                if severity in ['critical', 'high']]

    def get_word_severity(self, word: str) -> str:
        """Get the severity level of a specific word"""
        # Check if it's explicitly marked as 'none' (should not be flagged)
        for category_dict in [self.criminal_offenses, self.hate_speech, self.violence,
                             self.harassment, self.profanity, self.spam_indicators, self.illegal_activities]:
            if word.lower() in category_dict and category_dict[word.lower()] == 'none':
                return 'none'
        return self.all_flagged_words.get(word.lower(), 'none')

    def get_stats(self) -> Dict[str, int]:
        """Get statistics about the flagged words database"""
        return {
            'total_words': len(self.all_flagged_words),
            'criminal_offenses': len(self.criminal_offenses),
            'hate_speech': len(self.hate_speech),
            'violence': len(self.violence),
            'harassment': len(self.harassment),
            'profanity': len(self.profanity),
            'spam': len(self.spam_indicators),
            'illegal': len(self.illegal_activities),
            'critical_words': len(self.get_critical_words()),
            'high_priority_words': len(self.get_high_priority_words())
        }


# Global instance
flagged_words_db = FlaggedWordsDatabase()


def moderate_text_content(content: str) -> Tuple[bool, float, List[str]]:
    """
    Moderate text content using the flagged words database

    Returns:
        Tuple of (flagged, score, reasons)
    """
    matched_words, score = flagged_words_db.check_content(content)

    # Enhanced scoring logic
    flagged = False
    reasons = []

    if matched_words:
        # Count critical and high priority words
        critical_count = sum(1 for word in matched_words
                           if flagged_words_db.get_word_severity(word) == 'critical')
        high_count = sum(1 for word in matched_words
                        if flagged_words_db.get_word_severity(word) == 'high')

        # Apply scoring rules
        if critical_count >= 1:
            score += critical_count * 0.5  # Additional penalty for critical words
            flagged = True
        elif high_count >= 2:
            score += 0.3
            flagged = True
        elif score >= 0.6:
            flagged = True

        reasons.append(f"Contains {len(matched_words)} flagged words: {', '.join(matched_words[:5])}")
        if len(matched_words) > 5:
            reasons[0] += f" (and {len(matched_words) - 5} more)"

    # Final flagging decision
    if score >= 0.8 or flagged:
        flagged = True

    return flagged, min(score, 1.0), reasons


if __name__ == "__main__":
    print("Flagged Words Database Statistics")
    print("=" * 40)

    stats = flagged_words_db.get_stats()
    for key, value in stats.items():
        print(f"{key.replace('_', ' ').title()}: {value}")

    print("\nTesting Content Moderation:")
    print("-" * 30)

    test_cases = [
        "spam kill violent",
        "This is a normal message",
        "I love peace and harmony",
        "harmless",
        "innocent and peaceful",
        "murder rape assault",
        "fuck shit damn"
    ]

    for test_content in test_cases:
        flagged, score, reasons = moderate_text_content(test_content)
        status = "FLAGGED" if flagged else "APPROVED"
        print(f"Content: '{test_content}'")
        print(f"Status: {status} (Score: {score:.2f})")
        if reasons:
            print(f"Reasons: {reasons[0]}")
        print()
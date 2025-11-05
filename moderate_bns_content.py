#!/usr/bin/env python3
"""
Bharatiya Nyaya Sanhita (BNS) Content Moderation Script
======================================================

This script takes data from bharathi_nyaya_sanhita.py, moderates each section
through the RL-powered API, and displays only the approved content with scores.

Features:
- Moderates all BNS sections automatically
- Displays only content that passes moderation
- Shows moderation scores and confidence levels
- Categorizes content by approval status
- Provides statistics on moderation results

Author: Legal Content Moderation System
Version: 1.0.0
"""

import requests
import json
import time
from typing import Dict, List, Any, Tuple
from bharathi_nyaya_sanhita import create_bns_database, BharatiyaNyayaSanhitaDatabase

API_BASE_URL = "http://localhost:8000/api"

class BNSContentModerator:
    """Moderates BNS content and displays approved sections"""

    def __init__(self):
        self.bns_db = create_bns_database()
        self.moderated_content = []
        self.rejected_content = []
        self.stats = {
            "total_sections": 0,
            "approved": 0,
            "rejected": 0,
            "avg_score": 0.0,
            "avg_confidence": 0.0
        }

    def moderate_section(self, section_num: str, section_data: Dict[str, str]) -> Tuple[bool, Dict[str, Any]]:
        """Moderate a single BNS section through the API"""

        content = f"BNS Section {section_num}: {section_data['title']}"

        try:
            response = requests.post(
                f"{API_BASE_URL}/moderate",
                json={
                    "content": content,
                    "content_type": "text",
                    "metadata": {
                        "source": "bharathi_nyaya_sanhita",
                        "section": section_num,
                        "category": section_data.get("category", "unknown"),
                        "act": "Bharatiya Nyaya Sanhita, 2023"
                    }
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                return True, result
            else:
                print(f"   API Error for Section {section_num}: {response.status_code}")
                return False, {"error": f"HTTP {response.status_code}"}

        except Exception as e:
            print(f"   Request failed for Section {section_num}: {str(e)}")
            return False, {"error": str(e)}

    def moderate_all_sections(self, max_sections: int = None) -> None:
        """Moderate all BNS sections"""

        print("Starting BNS Content Moderation")
        print("=" * 50)

        sections_to_process = list(self.bns_db.bns_sections.items())

        if max_sections:
            sections_to_process = sections_to_process[:max_sections]

        self.stats["total_sections"] = len(sections_to_process)

        for section_num, section_data in sections_to_process:
            print(f"\nModerating Section {section_num}: {section_data['title'][:50]}...")

            success, result = self.moderate_section(section_num, section_data)

            if success and "flagged" in result:
                moderated_item = {
                    "section_number": section_num,
                    "title": section_data["title"],
                    "category": section_data.get("category", "unknown"),
                    "moderation_result": result,
                    "moderated_at": result.get("timestamp", "unknown")
                }

                if result["flagged"]:
                    self.rejected_content.append(moderated_item)
                    self.stats["rejected"] += 1
                    print(f"   REJECTED - Score: {result['score']:.3f}, Confidence: {result['confidence']:.3f}")
                    if result.get("reasons"):
                        print(f"   Reasons: {', '.join(result['reasons'])}")
                else:
                    self.moderated_content.append(moderated_item)
                    self.stats["approved"] += 1
                    print(f"   APPROVED - Score: {result['score']:.3f}, Confidence: {result['confidence']:.3f}")
            else:
                # If API fails, treat as rejected for safety
                self.rejected_content.append({
                    "section_number": section_num,
                    "title": section_data["title"],
                    "category": section_data.get("category", "unknown"),
                    "moderation_result": result,
                    "moderated_at": "failed"
                })
                self.stats["rejected"] += 1
                print(f"   MODERATION FAILED - {result.get('error', 'Unknown error')}")

            # Brief pause to avoid overwhelming the API
            time.sleep(0.1)

        # Calculate statistics
        if self.moderated_content:
            scores = [item["moderation_result"]["score"] for item in self.moderated_content]
            confidences = [item["moderation_result"]["confidence"] for item in self.moderated_content]
            self.stats["avg_score"] = sum(scores) / len(scores)
            self.stats["avg_confidence"] = sum(confidences) / len(confidences)

    def display_moderated_content(self) -> None:
        """Display only the approved (moderated) content"""

        print("\n" + "="*80)
        print("APPROVED BNS SECTIONS (Safe for Display)")
        print("="*80)

        if not self.moderated_content:
            print("No sections were approved for display.")
            return

        # Group by category
        categories = {}
        for item in self.moderated_content:
            cat = item["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(item)

        for category, items in categories.items():
            print(f"\nCategory: {category.upper()}")
            print("-" * (len(category) + 12))

            for item in sorted(items, key=lambda x: int(x["section_number"])):
                result = item["moderation_result"]
                print(f"\nSection {item['section_number']}: {item['title']}")
                print(f"   Status: APPROVED")
                print(f"   Score: {result['score']:.3f}")
                print(f"   Confidence: {result['confidence']:.1f}%")
                print(f"   Reasons: {', '.join(result.get('reasons', ['None']))}")
                print(f"   Moderated: {item['moderated_at']}")

    def display_statistics(self) -> None:
        """Display moderation statistics"""

        print("\n" + "="*80)
        print("MODERATION STATISTICS")
        print("="*80)

        print(f"Total Sections Processed: {self.stats['total_sections']}")
        print(f"Approved Sections: {self.stats['approved']} ({self.stats['approved']/self.stats['total_sections']*100:.1f}%)")
        print(f"Rejected Sections: {self.stats['rejected']} ({self.stats['rejected']/self.stats['total_sections']*100:.1f}%)")

        if self.moderated_content:
            print(f"Average Score: {self.stats['avg_score']:.3f}")
            print(f"Average Confidence: {self.stats['avg_confidence']:.1f}%")

        # Category breakdown
        if self.moderated_content:
            print("\nApproved by Category:")
            category_stats = {}
            for item in self.moderated_content:
                cat = item["category"]
                category_stats[cat] = category_stats.get(cat, 0) + 1

            for cat, count in sorted(category_stats.items()):
                print(f"   - {cat}: {count} sections")

    def save_results(self, filename: str = "bns_moderation_results.json") -> None:
        """Save moderation results to JSON file"""

        results = {
            "metadata": {
                "source": "bharathi_nyaya_sanhita.py",
                "moderation_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "api_endpoint": API_BASE_URL
            },
            "statistics": self.stats,
            "approved_content": self.moderated_content,
            "rejected_content": self.rejected_content
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\nResults saved to {filename}")

def main():
    """Main function to run BNS content moderation"""

    print("BNS Content Moderation System")
    print("=================================")

    # Check if API is running
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ API health check failed. Please ensure the server is running.")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API: {str(e)}")
        print("💡 Make sure the server is running with: python -m app.main")
        return

    print("✅ API connection successful")

    # Initialize moderator
    moderator = BNSContentModerator()

    # Moderate all sections (or limit for testing)
    max_sections = None  # Set to a number like 50 for testing, None for all
    moderator.moderate_all_sections(max_sections)

    # Display results
    moderator.display_statistics()
    moderator.display_moderated_content()

    # Save results
    moderator.save_results()

    print("\n🎉 Moderation complete! Only approved content is displayed above.")
    print("📄 Full results saved to bns_moderation_results.json")

if __name__ == "__main__":
    main()
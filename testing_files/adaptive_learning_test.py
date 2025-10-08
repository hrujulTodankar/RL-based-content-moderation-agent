"""
Adaptive Learning Test - Simulate 20 feedback events and visualize learning
"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def run_adaptive_learning_test():
    """Run 20 iterations of feedback to demonstrate learning"""
    
    print("=" * 70)
    print("ADAPTIVE RL LEARNING TEST - 20 Iterations")
    print("=" * 70)
    print()
    
    # Test content samples
    test_samples = [
        {"content": "spam spam spam click here now!!!", "expected": "flagged", "feedback": "thumbs_up"},
        {"content": "This is a wonderful product!", "expected": "clean", "feedback": "thumbs_up"},
        {"content": "hate hate kill violent abuse", "expected": "flagged", "feedback": "thumbs_up"},
        {"content": "Great service, highly recommend", "expected": "clean", "feedback": "thumbs_up"},
        {"content": "buy now click here spam", "expected": "flagged", "feedback": "thumbs_down"},  # False positive
    ]
    
    results = []
    
    for iteration in range(20):
        print(f"\n--- Iteration {iteration + 1}/20 ---")
        
        # Select test sample (cycle through)
        sample = test_samples[iteration % len(test_samples)]
        
        # Moderate content
        mod_response = requests.post(
            f"{BASE_URL}/moderate",
            json={
                "content": sample["content"],
                "content_type": "text"
            }
        )
        
        if mod_response.status_code != 200:
            print(f"❌ Moderation failed: {mod_response.status_code}")
            continue
        
        mod_data = mod_response.json()
        moderation_id = mod_data["moderation_id"]
        
        print(f"Content: {sample['content'][:40]}...")
        print(f"Flagged: {mod_data['flagged']}")
        print(f"Score: {mod_data['score']:.3f}")
        print(f"Confidence: {mod_data['confidence']:.3f}")
        
        # Submit feedback
        feedback_response = requests.post(
            f"{BASE_URL}/feedback",
            json={
                "moderation_id": moderation_id,
                "feedback_type": sample["feedback"],
                "rating": 5 if sample["feedback"] == "thumbs_up" else 2
            }
        )
        
        if feedback_response.status_code == 200:
            fb_data = feedback_response.json()
            print(f"Feedback: {sample['feedback']} (reward: {fb_data['reward_value']:.2f})")
            
            results.append({
                "iteration": iteration + 1,
                "score": mod_data["score"],
                "confidence": mod_data["confidence"],
                "reward": fb_data["reward_value"],
                "flagged": mod_data["flagged"]
            })
        else:
            print(f"❌ Feedback failed: {feedback_response.status_code}")
        
        time.sleep(0.5)  # Small delay between iterations
    
    # Generate learning report
    print("\n" + "=" * 70)
    print("GENERATING LEARNING REPORT...")
    print("=" * 70)
    
    # Note: This endpoint requires JWT token in production
    # For testing, use without auth or generate test token
    report_response = requests.post(f"{BASE_URL}/learning/report")
    
    if report_response.status_code == 200:
        report_data = report_response.json()
        print(f"\n✓ Report generated: {report_data['report_path']}")
        print(f"\nSummary Statistics:")
        summary = report_data['summary']
        print(f"  Total Iterations: {summary['total_iterations']}")
        print(f"  Total Reward: {summary['total_reward']:.2f}")
        print(f"  Avg Reward: {summary['avg_reward']:.3f}")
        print(f"  Reward Improvement: {summary['reward_improvement']:.1f}%")
        print(f"  Avg Confidence: {summary['avg_confidence']:.3f}")
        print(f"  Confidence Improvement: {summary['confidence_improvement']:.1f}%")
        print(f"  Accuracy: {summary['accuracy'] * 100:.1f}%")
    else:
        print(f"\n⚠️  Could not generate report (may require auth)")
        print(f"   Status code: {report_response.status_code}")
    
    # Display results table
    print("\n" + "=" * 70)
    print("LEARNING PROGRESS TABLE")
    print("=" * 70)
    print(f"{'Iter':<6}{'Score':<10}{'Confidence':<12}{'Reward':<10}{'Flagged':<10}")
    print("-" * 70)
    
    for r in results:
        print(f"{r['iteration']:<6}{r['score']:<10.3f}{r['confidence']:<12.3f}"
              f"{r['reward']:<10.2f}{'Yes' if r['flagged'] else 'No':<10}")
    
    # Calculate improvements
    if len(results) >= 10:
        first_half = results[:10]
        second_half = results[10:]
        
        first_avg_confidence = sum(r['confidence'] for r in first_half) / len(first_half)
        second_avg_confidence = sum(r['confidence'] for r in second_half) / len(second_half)
        
        improvement = ((second_avg_confidence - first_avg_confidence) / first_avg_confidence) * 100
        
        print("\n" + "=" * 70)
        print("LEARNING ANALYSIS")
        print("=" * 70)
        print(f"First 10 iterations avg confidence: {first_avg_confidence:.3f}")
        print(f"Last 10 iterations avg confidence: {second_avg_confidence:.3f}")
        print(f"Improvement: {improvement:+.1f}%")
        
        if improvement > 0:
            print("\n✓ System is learning and improving!")
        else:
            print("\n⚠️  System needs more diverse training data")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE!")
    print("=" * 70)
    print(f"\nCheck reports/learning_cycle.png for visualization")
    print(f"Check reports/learning_data.json for raw data")

if __name__ == "__main__":
    try:
        run_adaptive_learning_test()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
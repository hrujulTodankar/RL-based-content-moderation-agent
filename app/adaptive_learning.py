import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import json
import os
from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class AdaptiveLearningVisualizer:
    """Visualize RL agent's adaptive learning over time"""
    
    def __init__(self, reports_dir: str = "reports"):
        self.reports_dir = reports_dir
        os.makedirs(reports_dir, exist_ok=True)
        
        self.learning_data = {
            "iterations": [],
            "rewards": [],
            "scores": [],
            "confidence": [],
            "false_positives": [],
            "false_negatives": [],
            "accuracy": []
        }
    
    def add_iteration(
        self,
        iteration: int,
        reward: float,
        score: float,
        confidence: float,
        is_false_positive: bool = False,
        is_false_negative: bool = False,
        is_correct: bool = True
    ):
        """Add a learning iteration data point"""
        self.learning_data["iterations"].append(iteration)
        self.learning_data["rewards"].append(reward)
        self.learning_data["scores"].append(score)
        self.learning_data["confidence"].append(confidence)
        self.learning_data["false_positives"].append(1 if is_false_positive else 0)
        self.learning_data["false_negatives"].append(1 if is_false_negative else 0)
        self.learning_data["accuracy"].append(1 if is_correct else 0)
    
    def generate_learning_cycle_report(self, filename: str = "learning_cycle.png"):
        """Generate comprehensive learning visualization"""
        if len(self.learning_data["iterations"]) == 0:
            logger.warning("No learning data to visualize")
            return
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        fig.suptitle('Adaptive RL Learning Cycle - Performance Over Time', 
                     fontsize=16, fontweight='bold')
        
        iterations = self.learning_data["iterations"]
        
        # Plot 1: Cumulative Rewards
        cumulative_rewards = np.cumsum(self.learning_data["rewards"])
        axes[0, 0].plot(iterations, cumulative_rewards, 'b-', linewidth=2)
        axes[0, 0].set_title('Cumulative Reward Progress')
        axes[0, 0].set_xlabel('Iteration')
        axes[0, 0].set_ylabel('Cumulative Reward')
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].axhline(y=0, color='r', linestyle='--', alpha=0.5)
        
        # Plot 2: Moderation Scores
        axes[0, 1].plot(iterations, self.learning_data["scores"], 'g-', linewidth=2, alpha=0.7)
        axes[0, 1].set_title('Moderation Scores Over Time')
        axes[0, 1].set_xlabel('Iteration')
        axes[0, 1].set_ylabel('Score')
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].axhline(y=0.5, color='orange', linestyle='--', alpha=0.5, label='Threshold')
        axes[0, 1].legend()
        
        # Plot 3: Confidence Evolution
        axes[0, 2].plot(iterations, self.learning_data["confidence"], 'purple', linewidth=2)
        axes[0, 2].set_title('Confidence Evolution')
        axes[0, 2].set_xlabel('Iteration')
        axes[0, 2].set_ylabel('Confidence')
        axes[0, 2].grid(True, alpha=0.3)
        axes[0, 2].fill_between(iterations, self.learning_data["confidence"], alpha=0.3)
        
        # Plot 4: False Positive Rate (Rolling Window)
        window_size = min(5, len(iterations))
        if len(self.learning_data["false_positives"]) >= window_size:
            fp_rate = self._rolling_mean(self.learning_data["false_positives"], window_size)
            axes[1, 0].plot(iterations[window_size-1:], fp_rate, 'r-', linewidth=2)
        axes[1, 0].set_title('False Positive Rate (Rolling Avg)')
        axes[1, 0].set_xlabel('Iteration')
        axes[1, 0].set_ylabel('FP Rate')
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].set_ylim([0, 1])
        
        # Plot 5: Accuracy Curve
        if len(self.learning_data["accuracy"]) >= window_size:
            accuracy_rolling = self._rolling_mean(self.learning_data["accuracy"], window_size)
            axes[1, 1].plot(iterations[window_size-1:], accuracy_rolling, 'darkgreen', linewidth=2)
        axes[1, 1].set_title('Accuracy Improvement')
        axes[1, 1].set_xlabel('Iteration')
        axes[1, 1].set_ylabel('Accuracy')
        axes[1, 1].grid(True, alpha=0.3)
        axes[1, 1].set_ylim([0, 1])
        axes[1, 1].axhline(y=0.8, color='gold', linestyle='--', alpha=0.5, label='Target (80%)')
        axes[1, 1].legend()
        
        # Plot 6: Reward Distribution
        axes[1, 2].hist(self.learning_data["rewards"], bins=15, 
                        color='skyblue', edgecolor='black', alpha=0.7)
        axes[1, 2].set_title('Reward Distribution')
        axes[1, 2].set_xlabel('Reward Value')
        axes[1, 2].set_ylabel('Frequency')
        axes[1, 2].grid(True, alpha=0.3, axis='y')
        axes[1, 2].axvline(x=0, color='r', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        
        # Save figure
        filepath = os.path.join(self.reports_dir, filename)
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Learning cycle report saved to: {filepath}")
        
        # Also save raw data as JSON
        self._save_json_report()
        
        return filepath
    
    def _rolling_mean(self, data: List[float], window: int) -> List[float]:
        """Calculate rolling mean"""
        return [
            np.mean(data[max(0, i-window+1):i+1]) 
            for i in range(window-1, len(data))
        ]
    
    def _save_json_report(self):
        """Save learning data as JSON"""
        json_path = os.path.join(self.reports_dir, "learning_data.json")
        
        # Calculate summary statistics
        summary = {
            "total_iterations": len(self.learning_data["iterations"]),
            "total_reward": sum(self.learning_data["rewards"]),
            "avg_reward": np.mean(self.learning_data["rewards"]) if self.learning_data["rewards"] else 0,
            "avg_score": np.mean(self.learning_data["scores"]) if self.learning_data["scores"] else 0,
            "avg_confidence": np.mean(self.learning_data["confidence"]) if self.learning_data["confidence"] else 0,
            "false_positive_count": sum(self.learning_data["false_positives"]),
            "false_negative_count": sum(self.learning_data["false_negatives"]),
            "accuracy": np.mean(self.learning_data["accuracy"]) if self.learning_data["accuracy"] else 0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        report = {
            "summary": summary,
            "data": self.learning_data
        }
        
        with open(json_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Learning data JSON saved to: {json_path}")
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics"""
        if not self.learning_data["iterations"]:
            return {}
        
        return {
            "total_iterations": len(self.learning_data["iterations"]),
            "total_reward": sum(self.learning_data["rewards"]),
            "avg_reward": np.mean(self.learning_data["rewards"]),
            "reward_improvement": self._calculate_improvement(self.learning_data["rewards"]),
            "avg_score": np.mean(self.learning_data["scores"]),
            "score_stability": np.std(self.learning_data["scores"]),
            "avg_confidence": np.mean(self.learning_data["confidence"]),
            "confidence_improvement": self._calculate_improvement(self.learning_data["confidence"]),
            "false_positive_rate": np.mean(self.learning_data["false_positives"]),
            "false_negative_rate": np.mean(self.learning_data["false_negatives"]),
            "accuracy": np.mean(self.learning_data["accuracy"])
        }
    
    def _calculate_improvement(self, data: List[float]) -> float:
        """Calculate improvement from first half to second half"""
        if len(data) < 4:
            return 0.0
        
        mid = len(data) // 2
        first_half_avg = np.mean(data[:mid])
        second_half_avg = np.mean(data[mid:])
        
        if first_half_avg == 0:
            return 0.0
        
        return ((second_half_avg - first_half_avg) / abs(first_half_avg)) * 100

# Global instance
visualizer = AdaptiveLearningVisualizer()
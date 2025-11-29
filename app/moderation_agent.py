import random
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import re
import os
import html
import time
from pathlib import Path

from flagged_words import flagged_words_db, moderate_text_content

logger = logging.getLogger(__name__)

class ModerationAgent:
    """Advanced RL-powered content moderation agent with MCP awareness and persistent learning"""

    def __init__(self, state_path: str = "agent_state.json"):
        self.state_path = state_path
        self.state_dim = 15  # Enhanced state space
        self.action_dim = 3  # Actions: approve, flag, review
        self.learning_rate = 0.01
        self.gamma = 0.99
        self.epsilon = 0.1

        # Enhanced Q-table: { state_key: { action: value } }
        self.q_table = {}
        self.max_q_table_size = 10000  # Dynamic limit based on available memory
        self.min_q_table_size = 5000   # Minimum size to maintain learning capacity
        self.memory_usage_threshold = 0.8  # 80% memory usage threshold
        self.access_times = {}  # Track last access time for LRU eviction
        self.update_frequency = {}  # Track update frequency for intelligent eviction
        self.compression_enabled = True  # Enable state compression for memory efficiency

        # Moderation history for learning
        self.history = []

        # Content registry for state generation
        self.contents: Dict[str, Dict] = {}

        # Replay buffer for batch learning
        self.replay_buffer: List[Dict] = []
        self.max_replay = 2000

        # Recent rewards for metrics
        self.recent_rewards: List[float] = []

        # Content type specific rules
        self.rules = {
            "text": self._moderate_text,
            "image": self._moderate_image,
            "audio": self._moderate_audio,
            "video": self._moderate_video,
            "code": self._moderate_code
        }

        # MCP confidence weights
        self.mcp_weights = {
            "nlp_confidence": 0.3,
            "conversion_quality": 0.25,
            "analytics_score": 0.25,
            "origin_service_trust": 0.2
        }

        # Load persistent state
        self._load_state()

        # Sync with database if available (disabled for demo)
        # self._sync_with_database()

        # Initialize memory monitoring
        self._initialize_memory_management()

        logger.info("ModerationAgent initialized with enhanced memory management")
    
    async def moderate(
        self,
        content: Any,
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main moderation method with enhanced RL decision-making and persistence
        """
        try:
            # Generate or get content ID for state tracking
            content_id = metadata.get("content_id") if metadata else None
            if not content_id:
                content_id = f"temp_{int(time.time() * 1000000)}"

            # Register content for enhanced learning
            self.register_content(content_id, content_type, metadata)

            # Apply content-specific rules
            rule_result = await self.rules[content_type](content, metadata)

            # Simple scoring without RL for now
            final_score = rule_result["score"]
            flagged = final_score > 0.4

            result = {
                "flagged": flagged,
                "score": final_score,
                "confidence": rule_result["confidence"],
                "reasons": rule_result["reasons"],
                "action": "flag" if flagged else "approve",
                "mcp_weighted_score": None,
                "state": [],
                "content_id": content_id,
                "state_key": "simple"
            }

            return result

        except Exception as e:
            logger.error(f"Moderation error: {str(e)}", exc_info=True)
            raise
    
    def _extract_state(
        self,
        content: Any,
        content_type: str,
        metadata: Optional[Dict[str, Any]]
    ) -> List[float]:
        """Extract feature vector from content and metadata"""
        state = [0.0] * self.state_dim
        
        # Content type encoding
        type_map = {"text": 0, "image": 1, "audio": 2, "video": 3, "code": 4}
        state[0] = type_map.get(content_type, 0)
        
        # Basic content features
        if content_type == "text":
            state[1] = len(str(content)) / 1000  # Normalized length
            state[2] = str(content).count('!') / 10  # Exclamation ratio
            state[3] = len(str(content).split()) / 100  # Word count
        elif content_type in ["image", "audio", "video"]:
            if isinstance(content, bytes):
                state[1] = len(content) / (1024 * 1024)  # Size in MB
        
        # MCP metadata features
        if metadata and "mcp" in metadata:
            mcp = metadata["mcp"]
            state[4] = mcp.get("nlp_confidence", 0)
            state[5] = mcp.get("conversion_quality", 0)
            state[6] = mcp.get("sentiment_score", 0.5)
            state[7] = mcp.get("toxicity_score", 0)
            state[8] = mcp.get("engagement_score", 0)
        
        # Historical performance
        if len(self.history) > 0:
            recent = self.history[-10:]
            scores = [h["result"]["score"] for h in recent]
            state[9] = (sum(scores) / len(scores)) if scores else 0.0
            actions = [h["action"] for h in recent]
            state[10] = (sum(actions) / len(actions)) if actions else 0.0
        
        # Additional features
        state[11] = datetime.utcnow().hour / 24  # Time of day
        state[12] = len(self.history) / 1000  # Experience
        
        return state
    
    async def _moderate_text(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Text-specific moderation rules using comprehensive flagged words database"""
        score = 0.0
        reasons = []

        text = str(content).lower()

        # Use the comprehensive flagged words database
        flagged, flagged_score, flagged_reasons = moderate_text_content(content)

        if flagged:
            score += flagged_score
            reasons.extend(flagged_reasons)

        # Additional checks for content patterns

        # Excessive caps
        if len(text) > 10:
            caps_ratio = sum(1 for c in content if c.isupper()) / len(content)
            if caps_ratio > 0.5:
                score += 0.2
                reasons.append("Excessive capitalization")

        # URL spam - increased sensitivity
        url_count = len(re.findall(r'http[s]?://\S+', text))
        if url_count > 1:  # Lower threshold
            score += 0.4
            reasons.append(f"Multiple URLs detected ({url_count}) - potential spam or phishing")

        # Repetition - increased sensitivity
        words = text.split()
        if len(words) > 3:  # Lower threshold
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.6:  # Lower threshold for uniqueness
                score += 0.3
                reasons.append("High repetition detected - potential spam content")

        # Check for specific dangerous patterns
        dangerous_patterns = [
            (r'\b(?:kill|murder|rape|assault|hate|violent)\b.*\b(?:kill|murder|rape|assault|hate|violent)\b', "Multiple violent terms detected"),
            (r'\b(?:spam|scam|fraud|fake)\b.*\b(?:spam|scam|fraud|fake)\b', "Multiple suspicious terms detected"),
            (r'\b(?:fuck|shit|cunt|motherfucker)\b', "Strong profanity detected")
        ]

        for pattern, reason in dangerous_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score += 0.3
                reasons.append(reason)

        confidence = 0.95 if flagged else (0.8 if len(reasons) > 0 else 0.7)

        return {
            "score": min(score, 1.0),
            "confidence": confidence,
            "reasons": reasons if reasons else ["Clean content"]
        }
    
    async def _moderate_image(
        self,
        content: bytes,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Enhanced image-specific moderation with detailed reasoning"""
        logger.debug(f"Image moderation metadata: {metadata}")
        score = 0.0
        reasons = []
        approval_reasons = []

        # File size analysis with detailed thresholds
        size_mb = len(content) / (1024 * 1024)
        if size_mb > 100:
            score += 0.8
            reasons.append(f"Extremely large file size ({size_mb:.2f}MB) - potential abuse or bandwidth waste")
        elif size_mb > 50:
            score += 0.5
            reasons.append(f"Very large file size ({size_mb:.2f}MB) - may cause performance issues")
        elif size_mb > 20:
            score += 0.2
            reasons.append(f"Large file size ({size_mb:.2f}MB) - consider optimization")
        else:
            approval_reasons.append(f"Appropriate file size ({size_mb:.2f}MB)")

        # File format validation and analysis
        if metadata and "filename" in metadata:
            filename = metadata["filename"].lower()
            # Check for suspicious file extensions
            suspicious_extensions = ['.exe', '.bat', '.cmd', '.scr', '.pif', '.com']
            if any(filename.endswith(ext) for ext in suspicious_extensions):
                score += 1.0
                reasons.append("Dangerous file extension disguised as image - potential malware")

            # Check for double extensions (attempted bypass)
            if filename.count('.') > 1:
                parts = filename.split('.')
                if len(parts) > 2:
                    score += 0.7
                    reasons.append("Multiple file extensions detected - potential security bypass attempt")

        # Image dimension analysis (if available)
        if metadata and "width" in metadata and "height" in metadata:
            width = metadata["width"]
            height = metadata["height"]

            # Check for extremely large dimensions
            if width > 10000 or height > 10000:
                score += 0.6
                reasons.append(f"Unusually large image dimensions ({width}x{height}) - potential abuse")

            # Check for extremely small dimensions (suspicious)
            if width < 10 or height < 10:
                score += 0.4
                reasons.append(f"Suspiciously small image dimensions ({width}x{height}) - may be corrupted or malicious")

            # Check aspect ratio (extremely unusual ratios)
            if width > 0 and height > 0:
                aspect_ratio = max(width, height) / min(width, height)
                if aspect_ratio > 50:
                    score += 0.3
                    reasons.append(f"Extreme aspect ratio ({aspect_ratio:.1f}:1) - unusual image format")

        # Content analysis using MCP metadata
        if metadata and "mcp_metadata" in metadata:
            mcp = metadata["mcp_metadata"]
            logger.debug(f"MCP metadata type: {type(mcp)}, value: {mcp}")

            # NSFW content detection
            if mcp is not None and isinstance(mcp, dict) and "nsfw_score" in mcp:
                nsfw_score = mcp["nsfw_score"]
                if nsfw_score > 0.9:
                    score += 0.9
                    reasons.append(f"High NSFW content detected (confidence: {nsfw_score:.2f}) - explicit material")
                elif nsfw_score > 0.7:
                    score += 0.6
                    reasons.append(f"Moderate NSFW content detected (confidence: {nsfw_score:.2f}) - adult content")
                elif nsfw_score > 0.5:
                    score += 0.3
                    reasons.append(f"Low NSFW content detected (confidence: {nsfw_score:.2f}) - borderline content")
                else:
                    approval_reasons.append("No NSFW content detected")

            # Violence detection
            if mcp is not None and isinstance(mcp, dict) and "violence_score" in mcp:
                violence_score = mcp["violence_score"]
                if violence_score > 0.8:
                    score += 0.8
                    reasons.append(f"High violence content detected (confidence: {violence_score:.2f}) - graphic violence")
                elif violence_score > 0.5:
                    score += 0.5
                    reasons.append(f"Moderate violence content detected (confidence: {violence_score:.2f}) - violent themes")
                else:
                    approval_reasons.append("No violence detected")

            # Hate speech detection
            if mcp is not None and isinstance(mcp, dict) and "hate_score" in mcp:
                hate_score = mcp["hate_score"]
                if hate_score > 0.7:
                    score += 0.7
                    reasons.append(f"Hate speech detected (confidence: {hate_score:.2f}) - discriminatory content")
                elif hate_score > 0.4:
                    score += 0.4
                    reasons.append(f"Potentially hateful content detected (confidence: {hate_score:.2f})")

            # Spam detection
            if mcp is not None and isinstance(mcp, dict) and "spam_score" in mcp:
                spam_score = mcp["spam_score"]
                if spam_score > 0.8:
                    score += 0.6
                    reasons.append(f"High spam content detected (confidence: {spam_score:.2f}) - promotional material")
                elif spam_score > 0.5:
                    score += 0.3
                    reasons.append(f"Moderate spam content detected (confidence: {spam_score:.2f})")

            # Quality assessment
            if mcp is not None and isinstance(mcp, dict) and "quality_score" in mcp:
                quality_score = mcp["quality_score"]
                if quality_score < 0.2:
                    score += 0.2
                    reasons.append(f"Very low quality image (score: {quality_score:.2f}) - potentially corrupted")
                elif quality_score > 0.8:
                    approval_reasons.append("High quality image content")

        # Determine final reasons based on score
        if score == 0.0:
            # Image was approved - provide positive reasons
            final_reasons = approval_reasons if approval_reasons else ["Image appears clean and appropriate"]
        else:
            # Image was flagged - provide detailed flagging reasons
            final_reasons = reasons

        # Adjust confidence based on available analysis
        if metadata and "mcp_metadata" in metadata:
            confidence = 0.85  # High confidence with MCP data
        elif size_mb > 0:
            confidence = 0.75  # Medium confidence with basic analysis
        else:
            confidence = 0.6   # Lower confidence with minimal analysis

        return {
            "score": min(score, 1.0),
            "confidence": confidence,
            "reasons": final_reasons
        }
    
    async def _moderate_audio(
        self,
        content: bytes,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Audio-specific moderation"""
        score = 0.0
        reasons = []
        
        # Duration check (from metadata)
        if metadata and "duration" in metadata:
            duration = metadata["duration"]
            if duration > 600:  # 10 minutes
                score += 0.2
                reasons.append(f"Long audio: {duration}s")
        
        # Use transcription if available in MCP
        if metadata and "mcp_metadata" in metadata:
            mcp = metadata["mcp_metadata"]
            if "transcription" in mcp:
                text_result = await self._moderate_text(
                    mcp["transcription"],
                    metadata
                )
                score = max(score, text_result["score"])
                reasons.extend(text_result["reasons"])
        
        confidence = 0.65
        return {
            "score": min(score, 1.0),
            "confidence": confidence,
            "reasons": reasons if reasons else ["Audio appears clean"]
        }
    
    async def _moderate_video(
        self,
        content: bytes,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Enhanced video-specific moderation with comprehensive analysis"""
        score = 0.0
        reasons = []
        approval_reasons = []

        # File size analysis with detailed thresholds
        size_mb = len(content) / (1024 * 1024)
        if size_mb > 1000:  # 1GB
            score += 0.9
            reasons.append(f"Extremely large video file ({size_mb:.2f}MB) - potential abuse or bandwidth waste")
        elif size_mb > 500:  # 500MB
            score += 0.6
            reasons.append(f"Very large video file ({size_mb:.2f}MB) - may cause performance issues")
        elif size_mb > 200:  # 200MB
            score += 0.3
            reasons.append(f"Large video file ({size_mb:.2f}MB) - consider compression")
        else:
            approval_reasons.append(f"Appropriate video file size ({size_mb:.2f}MB)")

        # Duration analysis
        duration_seconds = 0
        if metadata and "duration" in metadata:
            duration_seconds = metadata["duration"]
            if duration_seconds > 3600:  # 1 hour
                score += 0.7
                reasons.append(f"Extremely long video ({duration_seconds/3600:.1f} hours) - potential spam")
            elif duration_seconds > 1800:  # 30 minutes
                score += 0.4
                reasons.append(f"Very long video ({duration_seconds/60:.1f} minutes) - may need review")
            elif duration_seconds > 600:  # 10 minutes
                score += 0.2
                reasons.append(f"Long video ({duration_seconds/60:.1f} minutes)")
            elif duration_seconds < 3:  # Too short
                score += 0.3
                reasons.append(f"Suspiciously short video ({duration_seconds:.1f}s) - may be corrupted or test content")

        # Video format validation
        if metadata and "filename" in metadata:
            filename = metadata["filename"].lower()
            # Check for suspicious extensions
            suspicious_extensions = ['.exe', '.bat', '.cmd', '.scr', '.pif', '.com']
            if any(filename.endswith(ext) for ext in suspicious_extensions):
                score += 1.0
                reasons.append("Dangerous file extension disguised as video - potential malware")

            # Check for double extensions
            if filename.count('.') > 1:
                parts = filename.split('.')
                if len(parts) > 2:
                    score += 0.7
                    reasons.append("Multiple file extensions detected - potential security bypass")

        # Advanced MCP metadata analysis
        if metadata and "mcp_metadata" in metadata:
            mcp = metadata["mcp_metadata"]

            # Video summary analysis (transcript/summary)
            if "summary" in mcp or "transcript" in mcp:
                text_content = mcp.get("summary") or mcp.get("transcript", "")
                if text_content:
                    summary_result = await self._moderate_text(text_content, metadata)
                    score = max(score, summary_result["score"] * 0.9)  # Higher weight for video content
                    reasons.extend([f"Content analysis: {r}" for r in summary_result["reasons"]])

            # Frame-by-frame analysis
            if "frame_scores" in mcp:
                frame_scores = mcp.get("frame_scores", [])
                if frame_scores:
                    avg_frame_score = sum(frame_scores) / len(frame_scores)
                    max_frame_score = max(frame_scores)

                    if max_frame_score > 0.9:
                        score += 0.8
                        reasons.append(f"Highly flagged content in video frames (max score: {max_frame_score:.2f})")
                    elif max_frame_score > 0.7:
                        score += 0.5
                        reasons.append(f"Moderately flagged content in video frames (max score: {max_frame_score:.2f})")
                    elif avg_frame_score > 0.5:
                        score += 0.3
                        reasons.append(f"Some flagged content in video frames (avg score: {avg_frame_score:.2f})")
                    else:
                        approval_reasons.append("Video frames appear clean")

            # Audio track analysis
            if "audio_score" in mcp:
                audio_score = mcp["audio_score"]
                if audio_score > 0.8:
                    score += 0.7
                    reasons.append(f"Flagged audio content detected (confidence: {audio_score:.2f})")
                elif audio_score > 0.5:
                    score += 0.4
                    reasons.append(f"Moderate audio concerns detected (confidence: {audio_score:.2f})")

            # Scene detection and analysis
            if "scene_scores" in mcp:
                scene_scores = mcp.get("scene_scores", [])
                if scene_scores:
                    high_scene_count = sum(1 for s in scene_scores if s > 0.7)
                    if high_scene_count > len(scene_scores) * 0.5:  # More than 50% flagged scenes
                        score += 0.6
                        reasons.append(f"Multiple problematic scenes detected ({high_scene_count}/{len(scene_scores)})")

            # Quality and technical analysis
            if "quality_score" in mcp:
                quality_score = mcp["quality_score"]
                if quality_score < 0.2:
                    score += 0.2
                    reasons.append(f"Very low video quality (score: {quality_score:.2f}) - potentially corrupted")
                elif quality_score > 0.8:
                    approval_reasons.append("High quality video content")

            # Motion and content analysis
            if "motion_score" in mcp:
                motion_score = mcp["motion_score"]
                # Unusual motion patterns might indicate problematic content
                if motion_score > 0.9:  # Extremely high motion
                    score += 0.1
                    reasons.append("Unusually high motion content detected")

        # Determine final reasons based on score
        if score == 0.0:
            final_reasons = approval_reasons if approval_reasons else ["Video content appears appropriate and clean"]
        else:
            final_reasons = reasons

        # Adjust confidence based on analysis depth
        if metadata and "mcp_metadata" in metadata:
            confidence = 0.85  # High confidence with comprehensive analysis
        elif duration_seconds > 0:
            confidence = 0.7   # Medium confidence with basic metadata
        else:
            confidence = 0.5   # Lower confidence with minimal analysis

        return {
            "score": min(score, 1.0),
            "confidence": confidence,
            "reasons": final_reasons
        }
    
    async def _moderate_code(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Code-specific moderation for malicious patterns"""
        score = 0.0
        reasons = []
        
        code = str(content).lower()
        
        # Check for dangerous patterns
        dangerous_patterns = [
            (r'eval\s*\(', "Use of eval()"),
            (r'exec\s*\(', "Use of exec()"),
            (r'__import__', "Dynamic imports"),
            (r'rm\s+-rf', "Destructive commands"),
            (r'drop\s+table', "SQL drop commands"),
            (r'delete\s+from', "SQL delete commands"),
            (r'system\s*\(', "System calls"),
            (r'subprocess', "Subprocess execution"),
        ]
        
        for pattern, reason in dangerous_patterns:
            if re.search(pattern, code):
                score += 0.3
                reasons.append(reason)
        
        # Check for obfuscation
        if len(code) > 100:
            readable_ratio = len(re.findall(r'\b\w{3,}\b', code)) / len(code.split())
            if readable_ratio < 0.3:
                score += 0.2
                reasons.append("Highly obfuscated code")
        
        confidence = 0.75
        return {
            "score": min(score, 1.0),
            "confidence": confidence,
            "reasons": reasons if reasons else ["Code appears safe"]
        }
    
    def _apply_mcp_weighting(
        self,
        base_score: float,
        mcp_metadata: Dict[str, Any]
    ) -> float:
        """Apply MCP cross-service confidence weighting"""
        weighted_score = base_score
        
        # NLP confidence adjustment
        nlp_conf = mcp_metadata.get("nlp_confidence", 0.5)
        weighted_score *= (0.7 + 0.3 * nlp_conf)
        
        # Conversion quality adjustment
        conversion_quality = mcp_metadata.get("conversion_quality", 0.5)
        weighted_score *= (0.8 + 0.2 * conversion_quality)
        
        # Analytics sentiment adjustment
        sentiment = mcp_metadata.get("sentiment_score", 0.5)
        if sentiment < 0.3:  # Negative sentiment
            weighted_score *= 1.2
        
        # Origin service trust
        origin_trust = mcp_metadata.get("origin_service_trust", 0.5)
        weighted_score *= (0.9 + 0.1 * origin_trust)
        
        return min(weighted_score, 1.0)
    
    def _select_action_enhanced(self, state_key: str, score: float) -> int:
        """Select action using enhanced epsilon-greedy policy with memory-aware Q-table"""
        # Track state access for memory management
        self._track_state_access(state_key)
        
        # Periodically optimize memory usage
        if random.random() < 0.1:  # 10% chance
            self._optimize_memory_usage()

        # Epsilon-greedy exploration
        if random.random() < self.epsilon:
            return random.randint(0, self.action_dim - 1)

        # Exploit: choose best action from enhanced Q-table
        if state_key in self.q_table:
            q_values = self.q_table[state_key]
            return max(range(len(q_values)), key=lambda i: q_values[str(i)])

        # Default based on score - adjusted for stricter flagging
        if score > 0.6:
            return 1  # Flag
        elif score > 0.3:
            return 2  # Review
        else:
            return 0  # Approve
    
    async def update_with_feedback(
        self,
        moderation_id: str,
        reward: float
    ):
        """Update Q-table with user feedback reward using enhanced learning"""
        try:
            # Clamp reward to reasonable bounds
            reward = max(-2.0, min(2.0, float(reward)))

            # Track recent rewards for metrics
            self.recent_rewards.append(reward)
            if len(self.recent_rewards) > 1000:
                self.recent_rewards.pop(0)

            # Find corresponding history entry
            for entry in reversed(self.history[-200:]):  # Look further back
                if entry.get("content_id") == moderation_id or entry.get("moderation_id") == moderation_id:
                    state_key = entry["state_key"]
                    action = entry["action"]

                    # Initialize Q-values if not exists
                    if state_key not in self.q_table:
                        self.q_table[state_key] = {str(i): 0.0 for i in range(self.action_dim)}

                    # Q-learning update with next state
                    old_q = self.q_table[state_key][str(action)]

                    # Use same state as next state for simplicity (could be enhanced)
                    next_state_key = state_key
                    if next_state_key in self.q_table:
                        max_q_next = max(self.q_table[next_state_key].values())
                    else:
                        max_q_next = 0.0

                    new_q = old_q + self.learning_rate * (reward + self.gamma * max_q_next - old_q)
                    self.q_table[state_key][str(action)] = max(-100.0, min(100.0, new_q))
                    
                    # Track update frequency for memory management
                    self.update_frequency[state_key] = self.update_frequency.get(state_key, 0) + 1
                    
                    # Periodically enforce size limits
                    if len(self.q_table) > self.max_q_table_size * 0.95:
                        self._enforce_q_table_size_limit()

                    logger.info(
                        f"Updated Q-value for state {state_key}, action {action}: "
                        f"{old_q:.3f} -> {new_q:.3f} (reward: {reward:.3f})"
                    )

                    # Update replay buffer with actual reward
                    for replay_entry in reversed(self.replay_buffer[-100:]):
                        if (replay_entry.get("content_id") == moderation_id or
                            replay_entry.get("moderation_id") == moderation_id):
                            replay_entry["reward"] = reward
                            break

                    # Perform batch learning occasionally
                    if random.random() < 0.3:  # 30% chance
                        self.batch_update_from_replay(batches=1, batch_size=32)

                    # Save state occasionally
                    if random.random() < 0.1:  # 10% chance
                        self._save_state()

                    # Send to RL Core for distributed learning
                    await self._send_to_rl_core(moderation_id, reward, entry["state"], action)
                    break

        except Exception as e:
            logger.error(f"Error updating with feedback: {str(e)}")

    async def _send_to_rl_core(
        self,
        moderation_id: str,
        reward: float,
        state: List[float],
        action: int
    ):
        """Send RL update to Omkar's RL Core service"""
        try:
            from integration_services import integration_services
            result = await integration_services.send_to_rl_core_update(
                moderation_id=moderation_id,
                reward=reward,
                state=state,
                action=action
            )
            if result["success"]:
                logger.info(f"RL Core update sent successfully for {moderation_id}")
            else:
                logger.warning(f"RL Core update failed: {result['error']}")
        except Exception as e:
            logger.error(f"Error sending to RL Core: {str(e)}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive agent statistics with memory management info"""
        # Calculate memory efficiency metrics
        total_accesses = sum(self.update_frequency.values()) if self.update_frequency else 0
        avg_access_frequency = total_accesses / len(self.q_table) if self.q_table else 0
        
        # Calculate Q-value distribution
        q_values = []
        for state_q_values in self.q_table.values():
            q_values.extend(state_q_values.values())
        
        return {
            "total_moderations": len(self.history),
            "q_table_size": len(self.q_table),
            "q_table_max_size": self.max_q_table_size,
            "q_table_utilization": round(len(self.q_table) / self.max_q_table_size * 100, 2) if self.max_q_table_size > 0 else 0,
            "epsilon": self.epsilon,
            "learning_rate": self.learning_rate,
            "replay_buffer_size": len(self.replay_buffer),
            "registered_contents": len(self.contents),
            "avg_recent_reward": round(sum(self.recent_rewards) / len(self.recent_rewards), 3) if self.recent_rewards else 0.0,
            "discount_factor": self.gamma,
            "memory_efficiency": {
                "avg_access_frequency": round(avg_access_frequency, 2),
                "total_state_accesses": total_accesses,
                "compression_enabled": self.compression_enabled,
                "memory_optimization_active": len(self.q_table) > self.min_q_table_size * 0.8
            },
            "q_value_stats": {
                "total_q_values": len(q_values),
                "avg_q_value": round(sum(q_values) / len(q_values), 3) if q_values else 0.0,
                "max_q_value": round(max(q_values), 3) if q_values else 0.0,
                "min_q_value": round(min(q_values), 3) if q_values else 0.0,
                "non_zero_q_values": sum(1 for q in q_values if abs(q) > 0.001)
            }
        }

    def register_content(self, content_id: str, content_type: str, metadata: Optional[Dict[str, Any]] = None):
        """Register content for enhanced state generation and learning"""
        safe_content_id = html.escape(str(content_id))
        safe_content_type = html.escape(str(content_type))

        # Extract features for state generation
        features = {
            "content_type": safe_content_type,
            "length": 0,
            "toxicity_score": 0.0,
            "authenticity_score": 0.5,
            "tags": []
        }

        if metadata:
            if "length" in metadata:
                features["length"] = max(0, min(10000, int(metadata["length"])))
            if "toxicity_score" in metadata:
                features["toxicity_score"] = max(0.0, min(1.0, float(metadata.get("toxicity_score", 0.0))))
            if "authenticity_score" in metadata:
                features["authenticity_score"] = max(0.0, min(1.0, float(metadata.get("authenticity_score", 0.5))))
            if "tags" in metadata:
                features["tags"] = [html.escape(str(tag)) for tag in metadata.get("tags", [])]

        self.contents[safe_content_id] = features

        # Initialize Q-value for this content's state
        state_key = self._generate_state_key(safe_content_id)
        if state_key not in self.q_table:
            self.q_table[state_key] = {str(i): 0.0 for i in range(self.action_dim)}

        logger.debug(f"Registered content {safe_content_id} with state key {state_key}")

    def _initialize_memory_management(self):
        """Initialize memory management system"""
        # Detect available memory and adjust Q-table size accordingly
        try:
            import psutil
            available_memory = psutil.virtual_memory().available
            # Reserve 10% of available memory for Q-table, with upper limit
            recommended_size = int((available_memory * 0.1) / (self.action_dim * 8))  # 8 bytes per float
            self.max_q_table_size = min(recommended_size, 50000)  # Cap at 50k entries
            self.min_q_table_size = max(5000, recommended_size // 4)  # At least 25% of max
            logger.info(f"Memory-aware Q-table sizing: max={self.max_q_table_size}, min={self.min_q_table_size}")
        except ImportError:
            # Fallback if psutil not available
            logger.info("Using default Q-table sizing (psutil not available)")
        except Exception as e:
            logger.warning(f"Could not detect memory: {e}, using defaults")

    def _enforce_q_table_size_limit(self):
        """Enhanced Q-table size management with intelligent eviction"""
        current_size = len(self.q_table)
        if current_size <= self.max_q_table_size:
            return

        # Calculate how many entries to remove
        entries_to_remove = current_size - self.max_q_table_size
        
        # Calculate eviction priorities based on multiple factors
        eviction_scores = []
        for state_key, q_values in self.q_table.items():
            # Calculate importance score for this state
            importance = self._calculate_state_importance(state_key, q_values)
            eviction_scores.append((state_key, importance))

        # Sort by importance (lower importance = higher eviction priority)
        eviction_scores.sort(key=lambda x: x[1])

        # Remove lowest importance states
        states_to_remove = [item[0] for item in eviction_scores[:entries_to_remove]]
        
        for state_key in states_to_remove:
            if state_key in self.q_table:
                del self.q_table[state_key]
            if state_key in self.access_times:
                del self.access_times[state_key]
            if state_key in self.update_frequency:
                del self.update_frequency[state_key]

        logger.info(f"Intelligent Q-table eviction: removed {entries_to_remove} entries. "
                   f"Current size: {len(self.q_table)}")

    def _calculate_state_importance(self, state_key: str, q_values: Dict[str, float]) -> float:
        """Calculate importance score for state eviction decisions"""
        importance = 0.0

        # Factor 1: Recent access (more recent = higher importance)
        access_time = self.access_times.get(state_key, 0)
        if access_time > 0:
            time_score = min(1.0, access_time / 1000.0)  # Normalize by 1000ms
            importance += time_score * 0.3

        # Factor 2: Update frequency (more frequent updates = higher importance)
        update_count = self.update_frequency.get(state_key, 0)
        if update_count > 0:
            freq_score = min(1.0, update_count / 10.0)  # Normalize by 10 updates
            importance += freq_score * 0.4

        # Factor 3: Q-value magnitude (higher absolute values = more learned = higher importance)
        max_q_value = max(abs(v) for v in q_values.values())
        value_score = min(1.0, max_q_value / 10.0)  # Normalize by Q-value range
        importance += value_score * 0.3

        return importance

    def _track_state_access(self, state_key: str):
        """Track state access for LRU-based eviction"""
        import time
        self.access_times[state_key] = time.time() * 1000  # Milliseconds
        
        # Update access frequency
        self.update_frequency[state_key] = self.update_frequency.get(state_key, 0) + 1

    def _optimize_memory_usage(self):
        """Periodic memory optimization"""
        current_size = len(self.q_table)
        
        # If we're close to the limit, proactively remove some entries
        if current_size > self.max_q_table_size * 0.9:
            # Remove states with very low importance (but not zero)
            low_importance_states = []
            for state_key, q_values in self.q_table.items():
                importance = self._calculate_state_importance(state_key, q_values)
                if importance < 0.1:  # Very low importance
                    low_importance_states.append((state_key, importance))
            
            # Remove bottom 5% of low-importance states
            states_to_remove = sorted(low_importance_states, key=lambda x: x[1])[:max(1, current_size // 20)]
            for state_key, _ in states_to_remove:
                if state_key in self.q_table:
                    del self.q_table[state_key]
                    if state_key in self.access_times:
                        del self.access_times[state_key]
                    if state_key in self.update_frequency:
                        del self.update_frequency[state_key]
            
            if states_to_remove:
                logger.debug(f"Proactive memory optimization: removed {len(states_to_remove)} low-importance states")

    def _generate_state_key(self, content_id: str) -> str:
        """Generate enhanced state key from content features"""
        if content_id not in self.contents:
            return "unknown_0_0_0"

        info = self.contents[content_id]
        content_type_map = {"text": 0, "image": 1, "audio": 2, "video": 3, "code": 4}
        type_code = content_type_map.get(info["content_type"], 0)

        # Bucketize features
        length_bucket = max(0, min(5, int(info["length"] / 2000)))  # 0-5 buckets
        toxicity_bucket = max(0, min(5, int(info["toxicity_score"] * 5)))  # 0-5 buckets
        authenticity_bucket = max(0, min(5, int(info["authenticity_score"] * 5)))  # 0-5 buckets

        return f"type_{type_code}_len_{length_bucket}_tox_{toxicity_bucket}_auth_{authenticity_bucket}"

    def _load_state(self):
        """Load persistent agent state from file"""
        if not os.path.exists(self.state_path):
            logger.info("No existing agent state found, starting fresh")
            return

        try:
            # Validate state path to prevent path traversal
            safe_path = Path(self.state_path).resolve()
            current_dir = Path.cwd().resolve()
            if not str(safe_path).startswith(str(current_dir)):
                raise ValueError("State file must be within the application's working directory.")

            if not str(safe_path).endswith('.json'):
                raise ValueError("State file must have .json extension")

            with open(safe_path, "r", encoding="utf-8") as f:
                state = json.load(f)

            self.q_table = state.get("q_table", {})
            self.epsilon = state.get("epsilon", self.epsilon)
            self.recent_rewards = state.get("recent_rewards", [])

            logger.info(f"Loaded agent state with {len(self.q_table)} Q-states")

        except (json.JSONDecodeError, IOError, KeyError, ValueError) as e:
            logger.warning(f"Could not load agent state: {e}")
            self.q_table = {}

    def _save_state(self):
        """Persist agent state to file with backup"""
        try:
            # Validate state path
            safe_path = Path(self.state_path).resolve()
            current_dir = Path.cwd().resolve()
            if not str(safe_path).startswith(str(current_dir)):
                raise ValueError("State file must be within the application's working directory.")

            if not str(safe_path).endswith('.json'):
                raise ValueError("State file must have .json extension")

            # Create backup
            if safe_path.exists():
                backup_path = safe_path.with_suffix('.json.bak')
                try:
                    if backup_path.exists():
                        backup_path.unlink()
                    safe_path.rename(backup_path)
                except (OSError, PermissionError):
                    pass  # Skip backup if file operations fail

            # Save new state
            state = {
                "q_table": self.q_table,
                "epsilon": self.epsilon,
                "recent_rewards": self.recent_rewards[-100:],  # Keep last 100 rewards
                "timestamp": datetime.utcnow().isoformat()
            }

            with open(safe_path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)

            logger.debug("Agent state saved successfully")

        except (IOError, OSError, ValueError) as e:
            logger.error(f"Could not save agent state: {e}")

    def _sync_with_database(self):
        """Sync agent with existing moderation database"""
        try:
            # Try to connect to the moderation database
            import sqlite3
            db_path = "logs/moderation.db"  # Based on the project structure

            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cur = conn.cursor()

                # Get recent moderations to register content
                cur.execute("""
                    SELECT moderation_id, content_type, score, timestamp
                    FROM moderations
                    ORDER BY timestamp DESC
                    LIMIT 100
                """)
                rows = cur.fetchall()
                conn.close()

                for row in rows:
                    moderation_id, content_type, score, timestamp = row
                    # Register content with basic metadata
                    self.register_content(
                        moderation_id,
                        content_type,
                        {"toxicity_score": score, "length": 100}  # Basic defaults
                    )

                logger.info(f"Synced {len(rows)} moderations from database")

        except Exception as e:
            logger.debug(f"Could not sync with database: {e}")

    def pretrain_from_examples(self, examples: List[Dict[str, Any]]):
        """Pretrain agent with labeled examples to seed Q-values"""
        if not isinstance(examples, list):
            raise ValueError("Examples must be a list")

        if len(examples) > 1000:
            raise ValueError("Too many examples for pretraining (max 1000)")

        logger.info(f"Pretraining agent with {len(examples)} examples")

        for i, example in enumerate(examples):
            try:
                if not isinstance(example, dict):
                    continue

                # Validate required fields
                required_fields = ['content_type', 'score', 'reward']
                for field in required_fields:
                    if field not in example:
                        raise ValueError(f"Missing required field: {field}")

                content_type = html.escape(str(example.get("content_type", "text")))
                score = max(0.0, min(1.0, float(example.get("score", 0.0))))
                reward = max(-2.0, min(2.0, float(example.get("reward", 0.0))))

                # Create synthetic content for state generation
                temp_id = f"pretrain_{i}_{int(score*100)}"
                metadata = {
                    "toxicity_score": score,
                    "length": example.get("length", 100),
                    "authenticity_score": example.get("authenticity", 0.5)
                }

                self.register_content(temp_id, content_type, metadata)
                state_key = self._generate_state_key(temp_id)

                # Seed Q-values based on reward
                if state_key not in self.q_table:
                    self.q_table[state_key] = {str(i): 0.0 for i in range(self.action_dim)}

                # Favor actions that would lead to correct moderation
                if reward > 0:  # Good moderation
                    if score > 0.5:  # High toxicity - should flag
                        self.q_table[state_key]["1"] += min(10.0, reward * 0.5)  # Flag action
                    else:  # Low toxicity - should approve
                        self.q_table[state_key]["0"] += min(10.0, reward * 0.5)  # Approve action
                else:  # Bad moderation
                    if score > 0.5:  # Should have flagged but didn't
                        self.q_table[state_key]["0"] -= min(10.0, abs(reward) * 0.3)  # Penalize approve
                    else:  # Should have approved but didn't
                        self.q_table[state_key]["1"] -= min(10.0, abs(reward) * 0.3)  # Penalize flag

            except (ValueError, TypeError, KeyError) as e:
                logger.warning(f"Skipping invalid pretraining example {i}: {e}")
                continue

        # Save updated state
        self._save_state()
        logger.info("Pretraining completed and state saved")

    def batch_update_from_replay(self, batches: int = 1, batch_size: int = 64):
        """Perform batch Q-learning updates from replay buffer"""
        if not self.replay_buffer:
            return

        for _ in range(batches):
            sample = random.sample(self.replay_buffer, min(batch_size, len(self.replay_buffer)))

            for experience in sample:
                state_key = experience["state"]
                action = str(experience["action"])
                reward = experience["reward"]
                next_state_key = experience["next_state"]

                if state_key not in self.q_table:
                    self.q_table[state_key] = {str(i): 0.0 for i in range(self.action_dim)}
                if next_state_key not in self.q_table:
                    self.q_table[next_state_key] = {str(i): 0.0 for i in range(self.action_dim)}

                # Q-learning update
                max_q_next = max(self.q_table[next_state_key].values())
                old_q = self.q_table[state_key][action]
                new_q = old_q + self.learning_rate * (reward + self.gamma * max_q_next - old_q)
                self.q_table[state_key][action] = max(-100.0, min(100.0, new_q))  # Bounds checking

        # Occasionally save state
        if random.random() < 0.1:
            self._save_state()
import random
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import re

from flagged_words import flagged_words_db, moderate_text_content

logger = logging.getLogger(__name__)

class ModerationAgent:
    """RL-powered content moderation agent with MCP awareness"""
    
    def __init__(self):
        self.state_dim = 15  # Enhanced state space
        self.action_dim = 3  # Actions: approve, flag, review
        self.learning_rate = 0.01
        self.gamma = 0.99
        self.epsilon = 0.1
        
        # Q-table for RL
        self.q_table = {}
        
        # Moderation history for learning
        self.history = []
        
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
        
        logger.info("ModerationAgent initialized")
    
    async def moderate(
        self,
        content: Any,
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main moderation method with RL decision-making
        """
        try:
            # Extract state from content and metadata
            state = self._extract_state(content, content_type, metadata)
            
            # Apply content-specific rules
            rule_result = await self.rules[content_type](content, metadata)
            
            # Apply MCP weighting if available
            mcp_weighted_score = None
            if metadata and "mcp" in metadata:
                mcp_weighted_score = self._apply_mcp_weighting(
                    rule_result["score"],
                    metadata["mcp"]
                )
                final_score = mcp_weighted_score
            else:
                final_score = rule_result["score"]
            
            # RL action selection
            action = self._select_action(state, final_score)
            
            # Determine if flagged based on action and score - lower threshold for flagged content
            flagged = action == 1 or final_score > 0.4  # Lowered from 0.5 to 0.4
            
            result = {
                "flagged": flagged,
                "score": final_score,
                "confidence": rule_result["confidence"],
                "reasons": rule_result["reasons"],
                "action": ["approve", "flag", "review"][action],
                "mcp_weighted_score": mcp_weighted_score,
                "state": state
            }
            
            # Store for learning
            self.history.append({
                "state": state,
                "action": action,
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            })
            
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
        """Video-specific moderation"""
        score = 0.0
        reasons = []
        
        # Size and duration checks
        size_mb = len(content) / (1024 * 1024)
        if size_mb > 500:
            score += 0.2
            reasons.append(f"Very large video: {size_mb:.2f}MB")
        
        # Use TTV (Text-to-Video) summary if available
        if metadata and "mcp_metadata" in metadata:
            mcp = metadata["mcp_metadata"]
            
            # Check video summary
            if "summary" in mcp:
                summary_result = await self._moderate_text(mcp["summary"], metadata)
                score = max(score, summary_result["score"] * 0.8)
                reasons.extend([f"Summary: {r}" for r in summary_result["reasons"]])
            
            # Check frame analysis
            if "frame_scores" in mcp:
                frame_scores = mcp.get("frame_scores", [])
                avg_frame_score = (sum(frame_scores) / len(frame_scores)) if frame_scores else 0.0
                if avg_frame_score > 0.7:
                    score += 0.4
                    reasons.append("Flagged content in frames")
        
        confidence = 0.6
        return {
            "score": min(score, 1.0),
            "confidence": confidence,
            "reasons": reasons if reasons else ["Video appears clean"]
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
    
    def _select_action(self, state: List[float], score: float) -> int:
        """Select action using epsilon-greedy policy"""
        state_key = tuple(round(x, 2) for x in state)
        
        # Epsilon-greedy exploration
        if random.random() < self.epsilon:
            return random.randint(0, self.action_dim - 1)
        
        # Exploit: choose best action from Q-table
        if state_key in self.q_table:
            values = self.q_table[state_key]
            return max(range(len(values)), key=lambda i: values[i])
        
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
        """Update Q-table with user feedback reward and send to RL Core"""
        try:
            # Find corresponding history entry
            for entry in reversed(self.history[-100:]):
                if "moderation_id" in entry and entry["moderation_id"] == moderation_id:
                    state = entry["state"]
                    action = entry["action"]

                    state_key = tuple(round(x, 2) for x in state)

                    # Initialize Q-values if not exists
                    if state_key not in self.q_table:
                        self.q_table[state_key] = [0.0] * self.action_dim

                    # Q-learning update
                    old_q = self.q_table[state_key][action]

                    # No next state in this simplified version
                    new_q = old_q + self.learning_rate * (reward - old_q)

                    self.q_table[state_key][action] = new_q

                    logger.info(
                        f"Updated Q-value for action {action}: "
                        f"{old_q:.3f} -> {new_q:.3f} (reward: {reward:.3f})"
                    )

                    # Send to RL Core for distributed learning
                    await self._send_to_rl_core(moderation_id, reward, state, action)
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
        """Get agent statistics"""
        return {
            "total_moderations": len(self.history),
            "q_table_size": len(self.q_table),
            "epsilon": self.epsilon,
            "learning_rate": self.learning_rate
        }
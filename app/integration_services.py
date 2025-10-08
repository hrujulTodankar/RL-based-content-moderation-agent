import httpx
import logging
from typing import Dict, Any, Optional
import os
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class IntegrationServices:
    """
    Integration with BHIV (Ashmit), RL Core (Omkar), and NLP (Aditya)
    Handles authentication and real-time feedback pipelines
    """
    
    def __init__(self):
        # Service URLs
        self.bhiv_url = os.getenv("BHIV_API_URL", "http://localhost:9001")
        self.rl_core_url = os.getenv("RL_CORE_API_URL", "http://localhost:9002")
        self.nlp_url = os.getenv("NLP_API_URL", "http://localhost:9003")
        
        # JWT Token for service-to-service communication
        self.service_token = os.getenv("SERVICE_JWT_TOKEN", "")
        
        # Timeout configuration
        self.timeout = httpx.Timeout(10.0, connect=5.0)
        
        # Performance metrics
        self.metrics = {
            "bhiv_calls": 0,
            "rl_core_calls": 0,
            "nlp_calls": 0,
            "total_latency": 0.0,
            "errors": 0
        }
        
        logger.info("IntegrationServices initialized")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with JWT token"""
        headers = {
            "Content-Type": "application/json"
        }
        if self.service_token:
            headers["Authorization"] = f"Bearer {self.service_token}"
        return headers
    
    async def send_to_bhiv_feedback(
        self,
        moderation_id: str,
        feedback_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send feedback to Ashmit's BHIV Analytics
        POST /bhiv/feedback
        """
        start_time = datetime.utcnow()
        self.metrics["bhiv_calls"] += 1
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "moderation_id": moderation_id,
                    "feedback_type": feedback_data.get("feedback_type"),
                    "rating": feedback_data.get("rating"),
                    "sentiment": feedback_data.get("sentiment", "neutral"),
                    "engagement_score": feedback_data.get("engagement_score", 0.5),
                    "timestamp": datetime.utcnow().isoformat(),
                    "metadata": feedback_data.get("metadata", {})
                }
                
                response = await client.post(
                    f"{self.bhiv_url}/bhiv/feedback",
                    json=payload,
                    headers=self._get_headers()
                )
                
                latency = (datetime.utcnow() - start_time).total_seconds()
                self.metrics["total_latency"] += latency
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"BHIV feedback sent successfully (latency: {latency:.3f}s)")
                    return {
                        "success": True,
                        "data": result,
                        "latency": latency
                    }
                else:
                    logger.warning(f"BHIV feedback failed: {response.status_code}")
                    self.metrics["errors"] += 1
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "latency": latency
                    }
                    
        except Exception as e:
            logger.error(f"Error sending to BHIV: {str(e)}")
            self.metrics["errors"] += 1
            return {
                "success": False,
                "error": str(e),
                "latency": (datetime.utcnow() - start_time).total_seconds()
            }
    
    async def send_to_rl_core_update(
        self,
        moderation_id: str,
        reward: float,
        state: Any,
        action: int
    ) -> Dict[str, Any]:
        """
        Send RL update to Omkar's RL Core
        POST /rl/update
        """
        start_time = datetime.utcnow()
        self.metrics["rl_core_calls"] += 1
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "moderation_id": moderation_id,
                    "reward": reward,
                    "state": state if isinstance(state, list) else state.tolist(),
                    "action": action,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                response = await client.post(
                    f"{self.rl_core_url}/rl/update",
                    json=payload,
                    headers=self._get_headers()
                )
                
                latency = (datetime.utcnow() - start_time).total_seconds()
                self.metrics["total_latency"] += latency
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"RL Core update successful (latency: {latency:.3f}s)")
                    return {
                        "success": True,
                        "data": result,
                        "latency": latency
                    }
                else:
                    logger.warning(f"RL Core update failed: {response.status_code}")
                    self.metrics["errors"] += 1
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "latency": latency
                    }
                    
        except Exception as e:
            logger.error(f"Error sending to RL Core: {str(e)}")
            self.metrics["errors"] += 1
            return {
                "success": False,
                "error": str(e),
                "latency": (datetime.utcnow() - start_time).total_seconds()
            }
    
    async def get_nlp_context(
        self,
        content: str,
        content_type: str
    ) -> Dict[str, Any]:
        """
        Get NLP context from Aditya's NLP service
        POST /nlp/context
        """
        start_time = datetime.utcnow()
        self.metrics["nlp_calls"] += 1
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "content": content,
                    "content_type": content_type,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                response = await client.post(
                    f"{self.nlp_url}/nlp/context",
                    json=payload,
                    headers=self._get_headers()
                )
                
                latency = (datetime.utcnow() - start_time).total_seconds()
                self.metrics["total_latency"] += latency
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"NLP context retrieved (latency: {latency:.3f}s)")
                    return {
                        "success": True,
                        "data": result,
                        "latency": latency
                    }
                else:
                    logger.warning(f"NLP context failed: {response.status_code}")
                    self.metrics["errors"] += 1
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "latency": latency,
                        "data": self._get_fallback_nlp_context()
                    }
                    
        except Exception as e:
            logger.error(f"Error getting NLP context: {str(e)}")
            self.metrics["errors"] += 1
            return {
                "success": False,
                "error": str(e),
                "latency": (datetime.utcnow() - start_time).total_seconds(),
                "data": self._get_fallback_nlp_context()
            }
    
    def _get_fallback_nlp_context(self) -> Dict[str, Any]:
        """Fallback NLP context when service is unavailable"""
        return {
            "confidence": 0.5,
            "toxicity": 0.0,
            "sentiment": 0.5,
            "language": "en",
            "context_embedding": []
        }
    
    async def execute_feedback_pipeline(
        self,
        moderation_id: str,
        feedback_data: Dict[str, Any],
        rl_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the full feedback pipeline:
        User Feedback → BHIV → RL Core → Analytics Log
        """
        pipeline_start = datetime.utcnow()
        results = {
            "moderation_id": moderation_id,
            "pipeline_steps": [],
            "total_latency": 0.0,
            "success": True
        }
        
        # Step 1: Send to BHIV
        bhiv_result = await self.send_to_bhiv_feedback(moderation_id, feedback_data)
        results["pipeline_steps"].append({
            "service": "BHIV",
            "success": bhiv_result["success"],
            "latency": bhiv_result["latency"]
        })
        
        # Step 2: Send to RL Core
        rl_result = await self.send_to_rl_core_update(
            moderation_id,
            rl_data["reward"],
            rl_data["state"],
            rl_data["action"]
        )
        results["pipeline_steps"].append({
            "service": "RL_Core",
            "success": rl_result["success"],
            "latency": rl_result["latency"]
        })
        
        # Calculate total latency
        total_latency = (datetime.utcnow() - pipeline_start).total_seconds()
        results["total_latency"] = total_latency
        results["success"] = bhiv_result["success"] and rl_result["success"]
        
        logger.info(f"Feedback pipeline completed (total latency: {total_latency:.3f}s)")
        
        return results
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get integration metrics"""
        avg_latency = (
            self.metrics["total_latency"] / 
            (self.metrics["bhiv_calls"] + self.metrics["rl_core_calls"] + self.metrics["nlp_calls"])
            if (self.metrics["bhiv_calls"] + self.metrics["rl_core_calls"] + self.metrics["nlp_calls"]) > 0
            else 0
        )
        
        return {
            **self.metrics,
            "avg_latency": avg_latency,
            "error_rate": self.metrics["errors"] / max(1, self.metrics["bhiv_calls"] + self.metrics["rl_core_calls"] + self.metrics["nlp_calls"])
        }

# Global instance
integration_services = IntegrationServices()
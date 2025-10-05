import asyncio
import logging
from typing import Dict, Any, Optional
import httpx
import os

logger = logging.getLogger(__name__)

class MCPIntegrator:
    """
    Integrates with Multi-Channel Pipelines (MCPs):
    - Omkar RL (conversion quality)
    - Aditya NLP (language models, confidence)
    - Ashmit BHIV analytics (sentiment, engagement)
    """
    
    def __init__(self):
        # Service endpoints (configure via environment)
        self.omkar_rl_url = os.getenv("OMKAR_RL_URL", "http://localhost:8001")
        self.aditya_nlp_url = os.getenv("ADITYA_NLP_URL", "http://localhost:8002")
        self.ashmit_analytics_url = os.getenv("ASHMIT_ANALYTICS_URL", "http://localhost:8003")
        
        # Timeout settings
        self.timeout = httpx.Timeout(10.0, connect=5.0)
        
        # Cache for recent results
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        logger.info("MCPIntegrator initialized")
    
    async def process(
        self,
        content: Any,
        content_type: str,
        mcp_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process content through MCP services and aggregate results
        """
        try:
            # Parallel processing of MCP services
            tasks = []
            
            # Omkar RL - Conversion quality
            if content_type in ["audio", "video", "image"]:
                tasks.append(self._query_omkar_rl(content, content_type, mcp_metadata))
            else:
                tasks.append(self._mock_omkar_result())
            
            # Aditya NLP - Text analysis and confidence
            if content_type in ["text", "code"] or "transcription" in mcp_metadata:
                text_content = content if content_type == "text" else mcp_metadata.get("transcription", "")
                tasks.append(self._query_aditya_nlp(text_content, mcp_metadata))
            else:
                tasks.append(self._mock_nlp_result())
            
            # Ashmit BHIV - Sentiment and engagement analytics
            tasks.append(self._query_ashmit_analytics(content, content_type, mcp_metadata))
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Aggregate results
            aggregated = {
                "omkar_rl": results[0] if not isinstance(results[0], Exception) else {},
                "aditya_nlp": results[1] if not isinstance(results[1], Exception) else {},
                "ashmit_analytics": results[2] if not isinstance(results[2], Exception) else {},
                "aggregated_confidence": 0.0,
                "aggregated_score": 0.0
            }
            
            # Calculate aggregated metrics
            aggregated.update(self._aggregate_metrics(aggregated))
            
            return aggregated
            
        except Exception as e:
            logger.error(f"MCP processing error: {str(e)}", exc_info=True)
            return self._fallback_result()
    
    async def _query_omkar_rl(
        self,
        content: Any,
        content_type: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Query Omkar's RL service for conversion quality"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.omkar_rl_url}/conversion_quality",
                    json={
                        "content_type": content_type,
                        "metadata": metadata
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "conversion_quality": result.get("quality_score", 0.5),
                        "rl_confidence": result.get("confidence", 0.5),
                        "processing_time": result.get("processing_time", 0)
                    }
                else:
                    logger.warning(f"Omkar RL returned {response.status_code}")
                    return self._mock_omkar_result()
                    
        except (httpx.RequestError, httpx.TimeoutException) as e:
            logger.warning(f"Omkar RL service unavailable: {str(e)}")
            return self._mock_omkar_result()
    
    async def _query_aditya_nlp(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Query Aditya's NLP service for text analysis"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.aditya_nlp_url}/analyze",
                    json={
                        "text": text,
                        "metadata": metadata
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "nlp_confidence": result.get("confidence", 0.5),
                        "toxicity_score": result.get("toxicity", 0.0),
                        "sentiment_score": result.get("sentiment", 0.5),
                        "language": result.get("language", "en"),
                        "model_version": result.get("model_version", "unknown")
                    }
                else:
                    logger.warning(f"Aditya NLP returned {response.status_code}")
                    return self._mock_nlp_result()
                    
        except (httpx.RequestError, httpx.TimeoutException) as e:
            logger.warning(f"Aditya NLP service unavailable: {str(e)}")
            return self._mock_nlp_result()
    
    async def _query_ashmit_analytics(
        self,
        content: Any,
        content_type: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Query Ashmit's BHIV analytics for engagement metrics"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.ashmit_analytics_url}/analyze_engagement",
                    json={
                        "content_type": content_type,
                        "metadata": metadata
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "engagement_score": result.get("engagement", 0.5),
                        "sentiment_score": result.get("sentiment", 0.5),
                        "predicted_rating": result.get("rating", 3.0),
                        "analytics_confidence": result.get("confidence", 0.5)
                    }
                else:
                    logger.warning(f"Ashmit Analytics returned {response.status_code}")
                    return self._mock_analytics_result()
                    
        except (httpx.RequestError, httpx.TimeoutException) as e:
            logger.warning(f"Ashmit Analytics service unavailable: {str(e)}")
            return self._mock_analytics_result()
    
    def _aggregate_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate metrics from all MCP services"""
        omkar = results.get("omkar_rl", {})
        aditya = results.get("aditya_nlp", {})
        ashmit = results.get("ashmit_analytics", {})
        
        # Weighted confidence calculation
        confidences = [
            omkar.get("rl_confidence", 0) * 0.25,
            aditya.get("nlp_confidence", 0) * 0.35,
            ashmit.get("analytics_confidence", 0) * 0.40
        ]
        aggregated_confidence = sum(confidences)
        
        # Weighted score (for risk/moderation)
        scores = []
        if "toxicity_score" in aditya:
            scores.append(aditya["toxicity_score"] * 0.4)
        if "conversion_quality" in omkar:
            # Lower quality = higher risk
            scores.append((1 - omkar["conversion_quality"]) * 0.3)
        if "sentiment_score" in ashmit:
            # Negative sentiment = higher risk
            scores.append((1 - ashmit["sentiment_score"]) * 0.3)
        
        aggregated_score = sum(scores) if scores else 0.0
        
        return {
            "aggregated_confidence": aggregated_confidence,
            "aggregated_score": aggregated_score,
            "origin_service_trust": 0.7  # Default trust level
        }
    
    # Mock results for when services are unavailable
    def _mock_omkar_result(self) -> Dict[str, Any]:
        """Mock result for Omkar RL service"""
        return {
            "conversion_quality": 0.7,
            "rl_confidence": 0.6,
            "processing_time": 0
        }
    
    def _mock_nlp_result(self) -> Dict[str, Any]:
        """Mock result for Aditya NLP service"""
        return {
            "nlp_confidence": 0.6,
            "toxicity_score": 0.1,
            "sentiment_score": 0.7,
            "language": "en",
            "model_version": "mock"
        }
    
    def _mock_analytics_result(self) -> Dict[str, Any]:
        """Mock result for Ashmit Analytics service"""
        return {
            "engagement_score": 0.5,
            "sentiment_score": 0.6,
            "predicted_rating": 3.5,
            "analytics_confidence": 0.5
        }
    
    def _fallback_result(self) -> Dict[str, Any]:
        """Fallback result when all services fail"""
        return {
            "omkar_rl": self._mock_omkar_result(),
            "aditya_nlp": self._mock_nlp_result(),
            "ashmit_analytics": self._mock_analytics_result(),
            "aggregated_confidence": 0.5,
            "aggregated_score": 0.2,
            "origin_service_trust": 0.5
        }
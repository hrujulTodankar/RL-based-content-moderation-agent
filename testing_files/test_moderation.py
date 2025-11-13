import pytest
import asyncio
from httpx import AsyncClient
from app.main import app
from app.moderation_agent import ModerationAgent
from app.feedback_handler import FeedbackHandler
import json

# Test fixtures
@pytest.fixture
async def client():
    """Create test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def moderation_agent():
    """Create moderation agent instance"""
    return ModerationAgent()

@pytest.fixture
async def feedback_handler():
    """Create feedback handler instance"""
    handler = FeedbackHandler()
    await handler.initialize()
    yield handler
    await handler.close()

# Test Cases

class TestModerationEndpoint:
    """Tests for /moderate endpoint"""
    
    @pytest.mark.asyncio
    async def test_moderate_text_clean(self, client):
        """Test moderating clean text content"""
        response = await client.post(
            "/moderate",
            json={
                "content": "This is a nice and friendly message",
                "content_type": "text"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "moderation_id" in data
        assert "flagged" in data
        assert "score" in data
        assert data["content_type"] == "text"
        assert data["score"] < 0.5  # Should be low risk
    
    @pytest.mark.asyncio
    async def test_moderate_text_flagged(self, client):
        """Test moderating text with flagged content"""
        response = await client.post(
            "/moderate",
            json={
                "content": "hate hate hate spam spam kill violent abuse",
                "content_type": "text"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["flagged"] == True
        assert data["score"] > 0.5
        assert len(data["reasons"]) > 0
    
    @pytest.mark.asyncio
    async def test_moderate_code_safe(self, client):
        """Test moderating safe code"""
        response = await client.post(
            "/moderate",
            json={
                "content": "def hello():\n    print('Hello, World!')\n    return 42",
                "content_type": "code"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["content_type"] == "code"
        assert data["score"] < 0.5
    
    @pytest.mark.asyncio
    async def test_moderate_code_dangerous(self, client):
        """Test moderating dangerous code"""
        response = await client.post(
            "/moderate",
            json={
                "content": "import os\nos.system('rm -rf /')\nexec('malicious code')",
                "content_type": "code"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["flagged"] == True
        assert data["score"] > 0.5
    
    @pytest.mark.asyncio
    async def test_moderate_with_mcp_metadata(self, client):
        """Test moderation with MCP metadata"""
        response = await client.post(
            "/moderate",
            json={
                "content": "Test content",
                "content_type": "text",
                "mcp_metadata": {
                    "nlp_confidence": 0.9,
                    "conversion_quality": 0.8,
                    "sentiment_score": 0.7
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "mcp_weighted_score" in data
    
    @pytest.mark.asyncio
    async def test_moderate_invalid_content_type(self, client):
        """Test with invalid content type"""
        response = await client.post(
            "/moderate",
            json={
                "content": "test",
                "content_type": "invalid_type"
            }
        )
        
        assert response.status_code == 400

class TestFeedbackEndpoint:
    """Tests for /feedback endpoint"""
    
    @pytest.mark.asyncio
    async def test_submit_thumbs_up_feedback(self, client):
        """Test submitting thumbs up feedback"""
        # First, create a moderation
        mod_response = await client.post(
            "/moderate",
            json={
                "content": "Test content",
                "content_type": "text"
            }
        )
        moderation_id = mod_response.json()["moderation_id"]
        
        # Submit feedback
        feedback_response = await client.post(
            "/feedback",
            json={
                "moderation_id": moderation_id,
                "feedback_type": "thumbs_up",
                "rating": 5
            }
        )
        
        assert feedback_response.status_code == 200
        data = feedback_response.json()
        assert "feedback_id" in data
        assert data["moderation_id"] == moderation_id
        assert data["reward_value"] > 0
    
    @pytest.mark.asyncio
    async def test_submit_thumbs_down_feedback(self, client):
        """Test submitting thumbs down feedback"""
        # First, create a moderation
        mod_response = await client.post(
            "/moderate",
            json={
                "content": "Test content",
                "content_type": "text"
            }
        )
        moderation_id = mod_response.json()["moderation_id"]
        
        # Submit feedback
        feedback_response = await client.post(
            "/feedback",
            json={
                "moderation_id": moderation_id,
                "feedback_type": "thumbs_down",
                "rating": 1,
                "comment": "This was incorrectly flagged"
            }
        )
        
        assert feedback_response.status_code == 200
        data = feedback_response.json()
        assert data["reward_value"] < 0
    
    @pytest.mark.asyncio
    async def test_invalid_feedback_type(self, client):
        """Test invalid feedback type"""
        response = await client.post(
            "/feedback",
            json={
                "moderation_id": "test_id",
                "feedback_type": "invalid_type"
            }
        )
        
        assert response.status_code == 400

class TestModerationAgent:
    """Tests for ModerationAgent class"""
    
    @pytest.mark.asyncio
    async def test_text_moderation_profanity(self, moderation_agent):
        """Test text moderation with profanity"""
        result = await moderation_agent.moderate(
            content="hate violence spam abuse kill",
            content_type="text"
        )
        
        assert result["score"] > 0.5
        assert result["flagged"] == True
        assert len(result["reasons"]) > 0
    
    @pytest.mark.asyncio
    async def test_text_moderation_clean(self, moderation_agent):
        """Test text moderation with clean content"""
        result = await moderation_agent.moderate(
            content="This is a wonderful day!",
            content_type="text"
        )
        
        assert result["score"] < 0.5
        assert len(result["reasons"]) >= 1
    
    @pytest.mark.asyncio
    async def test_code_moderation_safe(self, moderation_agent):
        """Test code moderation with safe code"""
        result = await moderation_agent.moderate(
            content="def add(a, b): return a + b",
            content_type="code"
        )
        
        assert result["score"] < 0.5
    
    @pytest.mark.asyncio
    async def test_code_moderation_dangerous(self, moderation_agent):
        """Test code moderation with dangerous code"""
        result = await moderation_agent.moderate(
            content="eval(input()); exec('dangerous')",
            content_type="code"
        )
        
        assert result["score"] > 0.5
        assert result["flagged"] == True
    
    @pytest.mark.asyncio
    async def test_mcp_weighting(self, moderation_agent):
        """Test MCP confidence weighting"""
        metadata = {
            "mcp": {
                "nlp_confidence": 0.9,
                "conversion_quality": 0.8,
                "sentiment_score": 0.6,
                "origin_service_trust": 0.7
            }
        }
        
        result = await moderation_agent.moderate(
            content="Test content",
            content_type="text",
            metadata=metadata
        )
        
        assert "mcp_weighted_score" in result
        assert result["mcp_weighted_score"] is not None

class TestFeedbackHandler:
    """Tests for FeedbackHandler class"""
    
    @pytest.mark.asyncio
    async def test_store_and_retrieve_moderation(self, feedback_handler):
        """Test storing and retrieving moderation records"""
        moderation_record = {
            "moderation_id": "test_mod_123",
            "content_type": "text",
            "flagged": False,
            "score": 0.3,
            "confidence": 0.8,
            "reasons": ["Clean content"],
            "timestamp": "2025-01-01T00:00:00"
        }
        
        await feedback_handler.store_moderation(moderation_record)
        
        # Verify storage (stats should reflect it)
        stats = await feedback_handler.get_statistics()
        assert stats["total_moderations"] >= 1
    
    @pytest.mark.asyncio
    async def test_store_and_retrieve_feedback(self, feedback_handler):
        """Test storing and retrieving feedback"""
        # First store a moderation
        moderation_record = {
            "moderation_id": "test_mod_456",
            "content_type": "text",
            "flagged": False,
            "score": 0.3,
            "confidence": 0.8,
            "reasons": ["Clean content"],
            "timestamp": "2025-01-01T00:00:00"
        }
        await feedback_handler.store_moderation(moderation_record)
        
        # Store feedback
        feedback_record = {
            "feedback_id": "test_fb_123",
            "moderation_id": "test_mod_456",
            "user_id": "user_1",
            "feedback_type": "thumbs_up",
            "rating": 5,
            "comment": "Great!",
            "reward_value": 0.8,
            "timestamp": "2025-01-01T00:01:00"
        }
        await feedback_handler.store_feedback(feedback_record)
        
        # Retrieve feedback
        feedbacks = await feedback_handler.get_feedback_by_moderation("test_mod_456")
        assert len(feedbacks) >= 1
        assert feedbacks[0]["feedback_type"] == "thumbs_up"
    
    @pytest.mark.asyncio
    async def test_normalize_feedback(self, feedback_handler):
        """Test feedback normalization"""
        # Thumbs up without rating
        reward1 = feedback_handler.normalize_feedback("thumbs_up")
        assert reward1 > 0
        
        # Thumbs up with high rating
        reward2 = feedback_handler.normalize_feedback("thumbs_up", rating=5)
        assert reward2 > 0
        
        # Thumbs down without rating
        reward3 = feedback_handler.normalize_feedback("thumbs_down")
        assert reward3 < 0
        
        # Thumbs down with low rating
        reward4 = feedback_handler.normalize_feedback("thumbs_down", rating=1)
        assert reward4 < 0
    
    @pytest.mark.asyncio
    async def test_get_statistics(self, feedback_handler):
        """Test statistics retrieval"""
        stats = await feedback_handler.get_statistics()
        
        assert "total_moderations" in stats
        assert "flagged_count" in stats
        assert "avg_score" in stats
        assert "total_feedback" in stats
        assert "content_types" in stats

class TestFileUpload:
    """Tests for file upload moderation"""
    
    @pytest.mark.asyncio
    async def test_moderate_image_file(self, client):
        """Test moderating an image file"""
        # Create a fake image file
        fake_image = b"fake image data" * 100
        
        files = {"file": ("test.jpg", fake_image, "image/jpeg")}
        data = {"content_type": "image"}
        
        response = await client.post(
            "/moderate/file",
            files=files,
            data=data
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["content_type"] == "image"

class TestHealthAndStats:
    """Tests for health and statistics endpoints"""
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check endpoint"""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data
    
    @pytest.mark.asyncio
    async def test_get_stats(self, client):
        """Test statistics endpoint"""
        response = await client.get("/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_moderations" in data

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
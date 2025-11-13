#!/usr/bin/env python3
"""
Comprehensive tests for the ModerationAgent with RL capabilities
"""

import pytest
import asyncio
import json
import os
import tempfile
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from app.moderation_agent import ModerationAgent


class TestModerationAgent:
    """Test suite for ModerationAgent"""

    def setup_method(self):
        """Setup test fixtures"""
        # Create temporary file for agent state
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()
        self.agent = ModerationAgent(state_path=self.temp_file.name)

    def teardown_method(self):
        """Cleanup test fixtures"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test agent initializes correctly"""
        assert self.agent.state_dim == 15
        assert self.agent.action_dim == 3
        assert self.agent.learning_rate == 0.01
        assert isinstance(self.agent.q_table, dict)
        assert isinstance(self.agent.history, list)
        assert isinstance(self.agent.contents, dict)

    @pytest.mark.asyncio
    async def test_content_registration(self):
        """Test content registration for enhanced learning"""
        content_id = "test_content_123"
        content_type = "text"
        metadata = {
            "toxicity_score": 0.3,
            "length": 150,
            "authenticity_score": 0.8
        }

        self.agent.register_content(content_id, content_type, metadata)

        assert content_id in self.agent.contents
        assert self.agent.contents[content_id]["content_type"] == content_type
        assert self.agent.contents[content_id]["toxicity_score"] == 0.3

        # Check Q-table initialization
        state_key = self.agent._generate_state_key(content_id)
        assert state_key in self.agent.q_table
        assert len(self.agent.q_table[state_key]) == self.agent.action_dim

    @pytest.mark.asyncio
    async def test_state_key_generation(self):
        """Test enhanced state key generation"""
        # Register content
        content_id = "test_123"
        self.agent.register_content(content_id, "text", {
            "toxicity_score": 0.7,
            "length": 500,
            "authenticity_score": 0.9
        })

        state_key = self.agent._generate_state_key(content_id)
        assert "type_0" in state_key  # text = 0
        assert "tox_4" in state_key   # 0.7 * 5 = 3.5 -> 4
        assert "auth_4" in state_key  # 0.9 * 5 = 4.5 -> 4

    @pytest.mark.asyncio
    async def test_text_moderation(self):
        """Test text content moderation"""
        content = "This is a clean test message"
        metadata = {"content_id": "text_test_123"}

        result = await self.agent.moderate(content, "text", metadata)

        assert "flagged" in result
        assert "score" in result
        assert "confidence" in result
        assert "reasons" in result
        assert "content_id" in result
        assert result["content_id"] == "text_test_123"

    @pytest.mark.asyncio
    async def test_image_moderation(self):
        """Test image content moderation"""
        # Mock image bytes
        image_bytes = b"mock image data" * 1000
        metadata = {
            "filename": "test.jpg",
            "width": 1920,
            "height": 1080,
            "mcp_metadata": {
                "nsfw_score": 0.1,
                "violence_score": 0.05,
                "quality_score": 0.9
            }
        }

        result = await self.agent.moderate(image_bytes, "image", metadata)

        assert "flagged" in result
        assert "score" in result
        assert "confidence" in result
        assert "reasons" in result
        assert result["score"] <= 1.0
        assert result["score"] >= 0.0

    @pytest.mark.asyncio
    async def test_video_moderation(self):
        """Test enhanced video content moderation"""
        video_bytes = b"mock video data" * 5000
        metadata = {
            "duration": 120,  # 2 minutes
            "filename": "test.mp4",
            "mcp_metadata": {
                "summary": "A test video about technology",
                "frame_scores": [0.1, 0.2, 0.1, 0.3],
                "audio_score": 0.1,
                "scene_scores": [0.1, 0.2, 0.1]
            }
        }

        result = await self.agent.moderate(video_bytes, "video", metadata)

        assert "flagged" in result
        assert "score" in result
        assert "confidence" in result
        assert "reasons" in result
        assert result["score"] <= 1.0

    @pytest.mark.asyncio
    async def test_code_moderation(self):
        """Test code content moderation"""
        code_content = """
        def safe_function():
            return "Hello World"

        # This is safe code
        result = safe_function()
        """

        result = await self.agent.moderate(code_content, "code")

        assert "flagged" in result
        assert "score" in result
        assert "reasons" in result
        assert "Code appears safe" in result["reasons"]

    @pytest.mark.asyncio
    async def test_dangerous_code_detection(self):
        """Test detection of dangerous code patterns"""
        dangerous_code = """
        import os
        os.system('rm -rf /')  # Dangerous!
        eval(user_input)       # Dangerous!
        """

        result = await self.agent.moderate(dangerous_code, "code")

        assert result["flagged"] == True
        assert result["score"] > 0.2
        assert len(result["reasons"]) > 0
        assert any("eval()" in reason for reason in result["reasons"])

    @pytest.mark.asyncio
    async def test_rl_action_selection(self):
        """Test RL action selection"""
        state_key = "test_state_key"
        self.agent.q_table[state_key] = {str(i): 0.5 for i in range(3)}

        action = self.agent._select_action_enhanced(state_key, 0.3)
        assert action in [0, 1, 2]

    @pytest.mark.asyncio
    async def test_feedback_learning(self):
        """Test RL learning from feedback"""
        # Create a moderation entry
        content_id = "feedback_test_123"
        await self.agent.moderate("Test content", "text", {"content_id": content_id})

        # Provide feedback
        reward = 1.0  # Positive feedback
        await self.agent.update_with_feedback(content_id, reward)

        # Check that recent rewards are tracked
        assert len(self.agent.recent_rewards) > 0
        assert reward in self.agent.recent_rewards

    @pytest.mark.asyncio
    async def test_batch_learning(self):
        """Test batch learning from replay buffer"""
        # Add some experiences to replay buffer
        for i in range(10):
            self.agent.replay_buffer.append({
                "state": f"state_{i}",
                "action": i % 3,
                "reward": 0.5,
                "next_state": f"state_{i+1}",
                "timestamp": 0
            })

        initial_q_size = len(self.agent.q_table)

        # Perform batch learning
        self.agent.batch_update_from_replay(batches=2, batch_size=5)

        # Q-table should have grown or been updated
        assert len(self.agent.q_table) >= initial_q_size

    def test_state_persistence(self):
        """Test agent state persistence"""
        # Add some Q-values
        self.agent.q_table["test_state"] = {"0": 0.8, "1": 0.2, "2": 0.5}
        self.agent.recent_rewards = [0.5, 0.7, 0.3]

        # Save state
        self.agent._save_state()

        # Create new agent instance
        new_agent = ModerationAgent(state_path=self.temp_file.name)

        # Check state was loaded
        assert "test_state" in new_agent.q_table
        assert new_agent.q_table["test_state"]["0"] == 0.8
        assert len(new_agent.recent_rewards) > 0

    @pytest.mark.asyncio
    async def test_pretraining(self):
        """Test agent pretraining with examples"""
        examples = [
            {
                "content_type": "text",
                "score": 0.8,
                "reward": 1.0,
                "length": 200
            },
            {
                "content_type": "text",
                "score": 0.2,
                "reward": -0.5,
                "length": 50
            }
        ]

        initial_q_size = len(self.agent.q_table)

        self.agent.pretrain_from_examples(examples)

        # Q-table should have grown
        assert len(self.agent.q_table) > initial_q_size

    def test_statistics(self):
        """Test agent statistics generation"""
        # Add some history
        self.agent.history = [
            {"state": "test", "action": 1, "result": {"score": 0.5}},
            {"state": "test2", "action": 0, "result": {"score": 0.2}}
        ]

        stats = self.agent.get_statistics()

        assert "total_moderations" in stats
        assert "q_table_size" in stats
        assert "replay_buffer_size" in stats
        assert "registered_contents" in stats
        assert stats["total_moderations"] == 2
        assert stats["q_table_size"] == len(self.agent.q_table)

    @pytest.mark.asyncio
    async def test_mcp_weighting(self):
        """Test MCP confidence weighting"""
        base_score = 0.5
        mcp_metadata = {
            "nlp_confidence": 0.9,
            "conversion_quality": 0.8,
            "sentiment_score": 0.2,  # Negative sentiment
            "origin_service_trust": 0.7
        }

        weighted_score = self.agent._apply_mcp_weighting(base_score, mcp_metadata)

        # Score should be adjusted based on MCP factors
        assert weighted_score != base_score
        assert 0.0 <= weighted_score <= 1.0

    @pytest.mark.asyncio
    async def test_concurrent_moderation(self):
        """Test concurrent moderation requests"""
        contents = [
            "Clean content 1",
            "Clean content 2",
            "Clean content 3",
            "Content with spam",
            "Another clean message"
        ]

        tasks = []
        for i, content in enumerate(contents):
            metadata = {"content_id": f"concurrent_test_{i}"}
            task = self.agent.moderate(content, "text", metadata)
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        assert len(results) == len(contents)
        for result in results:
            assert "flagged" in result
            assert "score" in result
            assert "content_id" in result

    @pytest.mark.asyncio
    async def test_large_content_handling(self):
        """Test handling of large content"""
        large_content = "word " * 10000  # 50,000 characters

        result = await self.agent.moderate(large_content, "text")

        assert "flagged" in result
        assert "score" in result
        # Should handle large content without crashing

    @pytest.mark.asyncio
    async def test_malformed_metadata_handling(self):
        """Test handling of malformed metadata"""
        content = "Test content"
        malformed_metadata = {
            "content_id": "test_123",
            "mcp": {
                "nlp_confidence": "not_a_number",  # Should handle gracefully
                "sentiment_score": None
            }
        }

        result = await self.agent.moderate(content, "text", malformed_metadata)

        # Should not crash and return valid result
        assert "flagged" in result
        assert "score" in result
        assert isinstance(result["score"], (int, float))

    def test_q_value_bounds_checking(self):
        """Test Q-value bounds checking"""
        state_key = "bounds_test"
        self.agent.q_table[state_key] = {"0": 0.0, "1": 0.0, "2": 0.0}

        # Manually set extreme values
        self.agent.q_table[state_key]["0"] = 1000  # Too high
        self.agent.q_table[state_key]["1"] = -1000  # Too low

        # Add to replay buffer
        self.agent.replay_buffer.append({
            "state": state_key,
            "action": 0,
            "reward": 1.0,
            "next_state": state_key,
            "timestamp": 0
        })

        # Perform batch update
        self.agent.batch_update_from_replay(batches=1, batch_size=1)

        # Values should be clamped
        assert -100 <= self.agent.q_table[state_key]["0"] <= 100
        assert -100 <= self.agent.q_table[state_key]["1"] <= 100
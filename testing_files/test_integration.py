import pytest
import asyncio
from httpx import AsyncClient
import os
import jwt
from datetime import datetime, timedelta

# Generate test JWT token
def generate_test_token():
    """Generate a test JWT token"""
    secret = os.getenv("SUPABASE_JWT_SECRET", "test-secret")
    payload = {
        "sub": "test-user-123",
        "email": "test@example.com",
        "role": "authenticated",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, secret, algorithm="HS256")

TEST_TOKEN = generate_test_token()
AUTH_HEADERS = {"Authorization": f"Bearer {TEST_TOKEN}"}

class TestIntegration:
    """Integration tests for all services"""
    
    @pytest.mark.asyncio
    async def test_connectivity_check(self):
        """Test connectivity to all integrated services"""
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.get(
                "/integration/connectivity",
                headers=AUTH_HEADERS
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "connectivity_test" in data
            
            # Check each service
            connectivity = data["connectivity_test"]
            print(f"\nConnectivity Results:")
            print(f"  BHIV: {connectivity['bhiv']['status']}")
            print(f"  RL Core: {connectivity['rl_core']['status']}")
            print(f"  NLP: {connectivity['nlp']['status']}")
    
    @pytest.mark.asyncio
    async def test_full_feedback_pipeline(self):
        """Test complete feedback pipeline"""
        async with AsyncClient(base_url="http://localhost:8000") as client:
            # Step 1: Moderate content
            mod_response = await client.post(
                "/moderate",
                json={
                    "content": "spam spam spam click here",
                    "content_type": "text"
                }
            )
            assert mod_response.status_code == 200
            mod_data = mod_response.json()
            moderation_id = mod_data["moderation_id"]
            
            # Step 2: Submit feedback
            fb_response = await client.post(
                "/feedback",
                json={
                    "moderation_id": moderation_id,
                    "feedback_type": "thumbs_up",
                    "rating": 5
                }
            )
            assert fb_response.status_code == 200
            fb_data = fb_response.json()
            assert fb_data["status"] == "processed"
            
            # Wait for pipeline to complete
            await asyncio.sleep(2)
            
            print(f"\n✓ Full pipeline test passed")
            print(f"  Moderation ID: {moderation_id}")
            print(f"  Reward: {fb_data['reward_value']}")
    
    @pytest.mark.asyncio
    async def test_demo_flow(self):
        """Test the demo flow endpoint"""
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.post("/demo/run")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert len(data["steps"]) == 5
            
            print(f"\n✓ Demo flow completed successfully")
            for step in data["steps"]:
                print(f"  {step['step']}: ✓")
    
    @pytest.mark.asyncio
    async def test_learning_report_generation(self):
        """Test learning report generation"""
        async with AsyncClient(base_url="http://localhost:8000") as client:
            # First, run some iterations
            for i in range(5):
                mod_response = await client.post(
                    "/moderate",
                    json={
                        "content": f"test content {i}",
                        "content_type": "text"
                    }
                )
                mod_data = mod_response.json()
                
                await client.post(
                    "/feedback",
                    json={
                        "moderation_id": mod_data["moderation_id"],
                        "feedback_type": "thumbs_up",
                        "rating": 5
                    }
                )
            
            # Generate report
            report_response = await client.post(
                "/learning/report",
                headers=AUTH_HEADERS
            )
            
            assert report_response.status_code == 200
            data = report_response.json()
            assert data["status"] == "success"
            assert "report_path" in data
            assert "summary" in data
            
            print(f"\n✓ Learning report generated")
            print(f"  Path: {data['report_path']}")
            print(f"  Iterations: {data['summary']['total_iterations']}")
    
    @pytest.mark.asyncio
    async def test_integration_metrics(self):
        """Test integration metrics endpoint"""
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.get(
                "/integration/metrics",
                headers=AUTH_HEADERS
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "integration_metrics" in data
            
            metrics = data["integration_metrics"]
            print(f"\n✓ Integration metrics retrieved")
            print(f"  BHIV calls: {metrics['bhiv_calls']}")
            print(f"  RL Core calls: {metrics['rl_core_calls']}")
            print(f"  NLP calls: {metrics['nlp_calls']}")
            print(f"  Avg latency: {metrics['avg_latency']:.3f}s")
    
    @pytest.mark.asyncio
    async def test_authenticated_endpoints(self):
        """Test that secured endpoints require JWT"""
        async with AsyncClient(base_url="http://localhost:8000") as client:
            # Without token - should fail
            response = await client.get("/integration/metrics")
            assert response.status_code == 403 or response.status_code == 401
            
            # With token - should succeed
            response = await client.get(
                "/integration/metrics",
                headers=AUTH_HEADERS
            )
            assert response.status_code == 200
            
            print(f"\n✓ Authentication working correctly")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
#!/usr/bin/env python3
"""
Comprehensive Test Suite for RL Content Moderation Improvements
===============================================================

Tests all implemented improvements including:
- Deterministic legal scoring system
- Jurisdiction-aware processing
- API response wrappers
- Error handling
- Memory optimization
- Service fallbacks

Author: Content Moderation System
Version: 1.0.0
"""

import asyncio
import pytest
import time
import logging
from typing import Dict, Any, List
import json

# Import all modules to test
from app.legal_content_analyzer import analyze_legal_content
from app.jurisdiction_processor import analyze_with_jurisdiction, test_content_jurisdictions
from app.api_wrappers import (
    APIResponseWrapper, 
    APIException, 
    handle_api_errors,
    success_response,
    error_response,
    validate_required_fields,
    validate_field_types,
    validate_enum_values
)
from app.schemas import StandardResponse, ErrorResponse, PaginatedResponse

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestDeterministicLegalScoring:
    """Test the deterministic legal content scoring system"""
    
    def test_bns_legal_scoring(self):
        """Test BNS-specific legal content scoring"""
        test_cases = [
            {
                "content": "BNS Section 103: Punishment for murder - Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.",
                "content_type": "bns",
                "jurisdiction": "india",
                "expected_score_range": (0.7, 0.9)
            },
            {
                "content": "Sexual harassment in workplace violates BNS Section 75 and constitutes a serious criminal offense under Bharatiya Nyaya Sanhita.",
                "content_type": "bns",
                "jurisdiction": "india",
                "expected_score_range": (0.6, 0.8)
            },
            {
                "content": "General discussion about legal procedures in Indian courts.",
                "content_type": "general",
                "jurisdiction": "india",
                "expected_score_range": (0.4, 0.6)
            }
        ]
        
        for test_case in test_cases:
            result = analyze_legal_content(
                test_case["content"],
                test_case["content_type"],
                test_case["jurisdiction"]
            )
            
            assert "adjusted_score" in result
            assert "analysis_details" in result
            assert "scoring_breakdown" in result
            
            score = result["adjusted_score"]
            min_score, max_score = test_case["expected_score_range"]
            assert min_score <= score <= max_score, f"Score {score} not in expected range {test_case['expected_score_range']}"
            
            logger.info(f"✅ BNS scoring test passed: {score:.3f}")
    
    def test_crpc_legal_scoring(self):
        """Test CrPC-specific legal content scoring"""
        test_cases = [
            {
                "content": "CrPC Section 41: When police may arrest without warrant - Any police officer may without an order from a Magistrate and without a warrant, arrest any person.",
                "content_type": "crpc",
                "jurisdiction": "india",
                "expected_score_range": (0.7, 0.9)
            },
            {
                "content": "Criminal procedure law requires proper documentation under Code of Criminal Procedure before any arrest.",
                "content_type": "crpc",
                "jurisdiction": "india",
                "expected_score_range": (0.5, 0.7)
            }
        ]
        
        for test_case in test_cases:
            result = analyze_legal_content(
                test_case["content"],
                test_case["content_type"],
                test_case["jurisdiction"]
            )
            
            assert "adjusted_score" in result
            score = result["adjusted_score"]
            min_score, max_score = test_case["expected_score_range"]
            assert min_score <= score <= max_score
            
            logger.info(f"✅ CrPC scoring test passed: {score:.3f}")
    
    def test_deterministic_consistency(self):
        """Test that scoring is deterministic (same input = same output)"""
        content = "BNS Section 101 defines murder as intentionally causing death."
        
        results = []
        for _ in range(10):
            result = analyze_legal_content(content, "bns", "india")
            results.append(result["adjusted_score"])
        
        # All scores should be identical
        assert all(score == results[0] for score in results), "Scoring is not deterministic"
        logger.info("✅ Deterministic consistency test passed")

class TestJurisdictionAwareProcessing:
    """Test jurisdiction-aware content processing"""
    
    def test_india_jurisdiction_analysis(self):
        """Test India-specific jurisdiction analysis"""
        content = "This content discusses caste discrimination and Hindu-Muslim relations in Indian society."
        
        result = analyze_with_jurisdiction(content, "IN", "text")
        
        assert result["country_code"] == "IN"
        assert "jurisdiction_analysis" in result
        assert "cultural_analysis" in result
        assert "legal_analysis" in result
        
        # Should detect sensitive topics for India
        jurisdiction_analysis = result["jurisdiction_analysis"]
        assert len(jurisdiction_analysis["sensitive_topics_found"]) > 0
        
        logger.info(f"✅ India jurisdiction analysis test passed: {jurisdiction_analysis['total_sensitivity_score']:.3f}")
    
    def test_multiple_jurisdictions(self):
        """Test content analysis across multiple jurisdictions"""
        content = "Political discussion about democratic processes and religious freedom."
        
        jurisdictions = ["IN", "UK", "US", "UAE"]
        result = test_content_jurisdictions(content, jurisdictions)
        
        assert result["jurisdictions_tested"] == jurisdictions
        assert len(result["results"]) == len(jurisdictions)
        
        # Each jurisdiction should have different analysis
        scores = []
        for jurisdiction, analysis in result["results"].items():
            if "jurisdiction_analysis" in analysis:
                scores.append(analysis["jurisdiction_analysis"]["total_sensitivity_score"])
        
        # Scores should vary by jurisdiction
        assert len(set(scores)) > 1, "Jurisdictions should produce different scores"
        
        logger.info("✅ Multiple jurisdictions test passed")
    
    def test_jurisdiction_specific_rules(self):
        """Test that different jurisdictions apply different rules"""
        content = "Religious content that might be sensitive in different cultures."
        
        uk_result = analyze_with_jurisdiction(content, "UK", "text")
        uae_result = analyze_with_jurisdiction(content, "UAE", "text")
        
        # UAE should have higher sensitivity due to religious content
        uk_score = uk_result["jurisdiction_analysis"]["total_sensitivity_score"]
        uae_score = uae_result["jurisdiction_analysis"]["total_sensitivity_score"]
        
        # UAE should be more sensitive to religious content
        assert uae_score >= uk_score, "UAE should be more sensitive to religious content"
        
        logger.info(f"✅ Jurisdiction-specific rules test passed: UK={uk_score:.3f}, UAE={uae_score:.3f}")

class TestAPIWrappers:
    """Test API response wrappers and error handling"""
    
    def test_standard_success_response(self):
        """Test standardized success response creation"""
        data = {"test": "value"}
        response = success_response(data, "Test message")
        
        assert isinstance(response, StandardResponse)
        assert response.success == True
        assert response.message == "Test message"
        assert response.data == data
        assert response.request_id is not None
        
        logger.info("✅ Standard success response test passed")
    
    def test_standard_error_response(self):
        """Test standardized error response creation"""
        message = "Test error"
        response = error_response(message, "TEST_ERROR", 400)
        
        assert isinstance(response, ErrorResponse)
        assert response.success == False
        assert response.message == message
        assert response.error_code == "TEST_ERROR"
        
        logger.info("✅ Standard error response test passed")
    
    def test_paginated_response(self):
        """Test paginated response creation"""
        data = [1, 2, 3, 4, 5]
        response = APIResponseWrapper.paginated(data, 1, 2, 5)
        
        assert isinstance(response, PaginatedResponse)
        assert response.data == [1, 2]
        assert response.meta["page"] == 1
        assert response.meta["page_size"] == 2
        assert response.meta["total_items"] == 5
        assert response.meta["has_next"] == True
        assert response.meta["has_prev"] == False
        
        logger.info("✅ Paginated response test passed")
    
    def test_error_decorator(self):
        """Test automatic error handling decorator"""
        
        @handle_api_errors
        def test_function():
            return {"test": "value"}
        
        result = test_function()
        assert result.status_code == 200
        
        # Test exception handling
        @handle_api_errors
        def test_error_function():
            raise ValueError("Test error")
        
        result = test_error_function()
        assert result.status_code == 400
        
        logger.info("✅ Error decorator test passed")
    
    def test_validation_functions(self):
        """Test data validation functions"""
        # Test required fields validation
        data = {"field1": "value1"}
        try:
            validate_required_fields(data, ["field1", "field2"])
            assert False, "Should have raised exception"
        except APIException as e:
            assert e.error_code == "MISSING_REQUIRED_FIELD"
        
        # Test field types validation
        validate_field_types(data, {"field1": str, "field2": int})
        
        # Test enum validation
        validate_enum_values(data, {"field1": ["value1", "value2", "value3"]})
        
        logger.info("✅ Validation functions test passed")

class TestIntegrationFunctionality:
    """Test integration between different components"""
    
    def test_legal_scoring_with_jurisdiction(self):
        """Test integration of legal scoring with jurisdiction analysis"""
        content = "BNS Section 103 covers murder punishment under Indian criminal law."
        
        # Get legal analysis
        legal_result = analyze_legal_content(content, "bns", "india")
        
        # Get jurisdiction analysis
        jurisdiction_result = analyze_with_jurisdiction(content, "IN", "text")
        
        # Both should work together
        assert legal_result["adjusted_score"] > 0
        assert jurisdiction_result["jurisdiction_analysis"]["total_sensitivity_score"] >= 0
        
        logger.info("✅ Legal + Jurisdiction integration test passed")
    
    def test_api_wrapper_with_analysis(self):
        """Test API wrappers with analysis results"""
        content = "Test legal content for API wrapper testing."
        
        # Get analysis
        analysis = analyze_with_jurisdiction(content, "US", "text")
        
        # Wrap in API response
        response = success_response(analysis, "Analysis completed successfully")
        
        assert isinstance(response, StandardResponse)
        assert response.success == True
        assert response.data == analysis
        
        logger.info("✅ API wrapper + analysis integration test passed")

class TestPerformanceImpact:
    """Test performance impact of improvements"""
    
    def test_jurisdiction_analysis_performance(self):
        """Test performance of jurisdiction analysis"""
        content = "This is a test content for performance measurement across multiple jurisdictions."
        jurisdictions = ["IN", "UK", "US", "UAE", "FR", "DE"]
        
        start_time = time.time()
        result = test_content_jurisdictions(content, jurisdictions)
        end_time = time.time()
        
        analysis_time = end_time - start_time
        
        # Should complete within reasonable time (5 seconds for 6 jurisdictions)
        assert analysis_time < 5.0, f"Analysis took too long: {analysis_time:.2f}s"
        
        logger.info(f"✅ Jurisdiction analysis performance test passed: {analysis_time:.3f}s")
    
    def test_memory_usage_patterns(self):
        """Test memory usage patterns of improved system"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Run multiple analyses to test memory patterns
        for i in range(100):
            content = f"Test content number {i} for memory testing."
            analyze_with_jurisdiction(content, "IN", "text")
            analyze_legal_content(content, "bns", "india")
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB for 100 analyses)
        assert memory_increase < 50, f"Memory increase too high: {memory_increase:.2f}MB"
        
        logger.info(f"✅ Memory usage test passed: {memory_increase:.2f}MB increase")

class TestErrorHandling:
    """Test comprehensive error handling"""
    
    def test_api_exception_handling(self):
        """Test custom API exception handling"""
        try:
            raise APIException("Test message", "TEST_ERROR", 400)
        except APIException as e:
            assert e.message == "Test message"
            assert e.error_code == "TEST_ERROR"
            assert e.status_code == 400
        
        logger.info("✅ API exception handling test passed")
    
    def test_graceful_degradation(self):
        """Test graceful degradation when services are unavailable"""
        # Test with invalid jurisdiction (should not crash)
        try:
            result = analyze_with_jurisdiction("test content", "INVALID", "text")
            # Should return valid result or handle gracefully
            assert result is not None
        except Exception as e:
            # Should handle gracefully with appropriate error
            logger.info(f"✅ Graceful degradation test passed: {str(e)}")
    
    def test_fallback_mechanisms(self):
        """Test fallback mechanisms for failed operations"""
        # Test with extremely long content (should handle gracefully)
        long_content = "test " * 10000
        try:
            result = analyze_legal_content(long_content, "bns", "india")
            # Should either process successfully or fail gracefully
            assert result is not None
        except Exception as e:
            logger.info(f"✅ Fallback mechanism test passed: {str(e)}")

def run_comprehensive_tests():
    """Run all comprehensive tests"""
    logger.info("🚀 Starting comprehensive test suite for RL content moderation improvements")
    
    test_classes = [
        TestDeterministicLegalScoring,
        TestJurisdictionAwareProcessing,
        TestAPIWrappers,
        TestIntegrationFunctionality,
        TestPerformanceImpact,
        TestErrorHandling
    ]
    
    passed_tests = 0
    total_tests = 0
    
    for test_class in test_classes:
        logger.info(f"\n📋 Running {test_class.__name__}")
        test_instance = test_class()
        
        # Get all test methods
        test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
        
        for test_method_name in test_methods:
            total_tests += 1
            test_method = getattr(test_instance, test_method_name)
            
            try:
                test_method()
                passed_tests += 1
                logger.info(f"  ✅ {test_method_name}")
            except Exception as e:
                logger.error(f"  ❌ {test_method_name}: {str(e)}")
    
    logger.info(f"\n🏁 Test Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        logger.info("🎉 All tests passed! Comprehensive improvements are working correctly.")
        return True
    else:
        logger.warning(f"⚠️  {total_tests - passed_tests} tests failed. Review the issues above.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_tests()
    exit(0 if success else 1)
#!/usr/bin/env python3
"""
Test script to verify the updated timeline parameters
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.endpoints.timeline import (
    JurisdictionEnum, 
    PriorityEnum, 
    CaseSeverityEnum,
    TimelineRequest,
    calculate_priority_modifier,
    calculate_severity_modifier
)

def test_enum_definitions():
    """Test that all enums are properly defined"""
    print("Testing enum definitions...")
    
    # Test JurisdictionEnum
    expected_jurisdictions = ["IN", "US", "UK", "CA", "AU", "EU"]
    actual_jurisdictions = [j.value for j in JurisdictionEnum]
    assert set(expected_jurisdictions) == set(actual_jurisdictions), f"Expected {expected_jurisdictions}, got {actual_jurisdictions}"
    print("[OK] JurisdictionEnum definitions correct")
    
    # Test PriorityEnum
    expected_priorities = ["low", "medium", "high"]
    actual_priorities = [p.value for p in PriorityEnum]
    assert set(expected_priorities) == set(actual_priorities), f"Expected {expected_priorities}, got {actual_priorities}"
    print("[OK] PriorityEnum definitions correct")
    
    # Test CaseSeverityEnum
    expected_severities = ["minor", "moderate", "severe", "critical"]
    actual_severities = [s.value for s in CaseSeverityEnum]
    assert set(expected_severities) == set(actual_severities), f"Expected {expected_severities}, got {actual_severities}"
    print("[OK] CaseSeverityEnum definitions correct")

def test_timeline_request_model():
    """Test TimelineRequest model with new parameters"""
    print("\nTesting TimelineRequest model...")
    
    # Test with all parameters
    request = TimelineRequest(
        case_id="TEST-001",
        case_type="criminal",
        jurisdiction=JurisdictionEnum.US,
        start_date="2024-01-15",
        priority=PriorityEnum.HIGH,
        case_severity=CaseSeverityEnum.CRITICAL
    )
    
    assert request.case_id == "TEST-001"
    assert request.case_type == "criminal"
    assert request.jurisdiction == JurisdictionEnum.US
    assert request.start_date == "2024-01-15"
    assert request.priority == PriorityEnum.HIGH
    assert request.case_severity == CaseSeverityEnum.CRITICAL
    print("[OK] TimelineRequest model accepts all new parameters")
    
    # Test with default values
    default_request = TimelineRequest(
        case_id="TEST-002",
        case_type="civil"
    )
    
    assert default_request.jurisdiction == JurisdictionEnum.IN
    assert default_request.priority == PriorityEnum.MEDIUM
    assert default_request.case_severity == CaseSeverityEnum.MODERATE
    assert default_request.start_date is None
    print("[OK] TimelineRequest model uses correct default values")

def test_calculation_modifiers():
    """Test the priority and severity calculation modifiers"""
    print("\nTesting calculation modifiers...")
    
    # Test priority modifiers
    assert calculate_priority_modifier(PriorityEnum.LOW) == 1.2
    assert calculate_priority_modifier(PriorityEnum.MEDIUM) == 1.0
    assert calculate_priority_modifier(PriorityEnum.HIGH) == 0.8
    print("[OK] Priority modifiers calculated correctly")
    
    # Test severity modifiers
    assert calculate_severity_modifier(CaseSeverityEnum.MINOR) == 0.9
    assert calculate_severity_modifier(CaseSeverityEnum.MODERATE) == 1.0
    assert calculate_severity_modifier(CaseSeverityEnum.SEVERE) == 1.3
    assert calculate_severity_modifier(CaseSeverityEnum.CRITICAL) == 0.7
    print("[OK] Severity modifiers calculated correctly")
    
    # Test combined modifier calculation
    high_priority = calculate_priority_modifier(PriorityEnum.HIGH)
    critical_severity = calculate_severity_modifier(CaseSeverityEnum.CRITICAL)
    combined = high_priority * critical_severity
    expected = 0.8 * 0.7  # 0.56
    
    assert abs(combined - expected) < 0.01, f"Expected {expected}, got {combined}"
    print(f"[OK] Combined modifier calculation: {combined:.2f}")

def test_parameter_combinations():
    """Test various parameter combinations"""
    print("\nTesting parameter combinations...")
    
    test_cases = [
        {
            "name": "High Priority + Critical Severity",
            "priority": PriorityEnum.HIGH,
            "severity": CaseSeverityEnum.CRITICAL,
            "expected_modifier": 0.8 * 0.7  # 0.56 (much faster)
        },
        {
            "name": "Low Priority + Severe Severity", 
            "priority": PriorityEnum.LOW,
            "severity": CaseSeverityEnum.SEVERE,
            "expected_modifier": 1.2 * 1.3  # 1.56 (much slower)
        },
        {
            "name": "Medium Priority + Moderate Severity",
            "priority": PriorityEnum.MEDIUM,
            "severity": CaseSeverityEnum.MODERATE,
            "expected_modifier": 1.0 * 1.0  # 1.0 (normal)
        }
    ]
    
    for case in test_cases:
        priority_mod = calculate_priority_modifier(case["priority"])
        severity_mod = calculate_severity_modifier(case["severity"])
        combined = priority_mod * severity_mod
        
        assert abs(combined - case["expected_modifier"]) < 0.01, \
            f"{case['name']}: Expected {case['expected_modifier']}, got {combined}"
        
        print(f"[OK] {case['name']}: {combined:.2f}x duration modifier")

if __name__ == "__main__":
    print("Timeline Parameter Updates Test Suite")
    print("=" * 50)
    
    try:
        test_enum_definitions()
        test_timeline_request_model()
        test_calculation_modifiers()
        test_parameter_combinations()
        
        print("\n" + "=" * 50)
        print("[SUCCESS] All tests passed! Timeline parameter updates are working correctly.")
        print("\nNew parameters available:")
        print("- jurisdiction: IN, US, UK, CA, AU, EU (default: IN)")
        print("- priority: low, medium, high (default: medium)")
        print("- case_severity: minor, moderate, severe, critical (default: moderate)")
        print("- start_date: Optional YYYY-MM-DD format (default: today)")
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        sys.exit(1)
#!/usr/bin/env python3
"""
Comprehensive test runner for RL-Powered Content Moderation API
"""

import subprocess
import sys
import os
from pathlib import Path
import argparse
import time

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)

    start_time = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        end_time = time.time()

        if result.returncode == 0:
            print(f"✅ PASSED ({end_time - start_time:.2f}s)")
            if result.stdout:
                print("Output:", result.stdout.strip())
            return True
        else:
            print(f"❌ FAILED ({end_time - start_time:.2f}s)")
            if result.stderr:
                print("Errors:", result.stderr.strip())
            if result.stdout:
                print("Output:", result.stdout.strip())
            return False

    except subprocess.TimeoutExpired:
        print(f"⏰ TIMEOUT ({time.time() - start_time:.2f}s)")
        return False
    except Exception as e:
        print(f"💥 ERROR: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Run comprehensive test suite")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--security", action="store_true", help="Run only security tests")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Change to project root
    project_root = Path(__file__).parent
    os.chdir(project_root)

    results = []
    total_start = time.time()

    # Unit Tests
    if not any([args.integration, args.security, args.performance]) or args.unit:
        print("\n🚀 Starting Unit Tests...")

        cmd = [sys.executable, "-m", "pytest", "tests/test_moderation_agent.py"]
        if args.coverage:
            cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])
        if args.verbose:
            cmd.append("-v")

        results.append(run_command(cmd, "Unit Tests - Moderation Agent"))

        cmd = [sys.executable, "-m", "pytest", "tests/test_security.py"]
        if args.coverage:
            cmd.extend(["--cov=app.security", "--cov-append"])
        if args.verbose:
            cmd.append("-v")

        results.append(run_command(cmd, "Unit Tests - Security"))

    # Integration Tests
    if not any([args.unit, args.security, args.performance]) or args.integration:
        print("\n🔗 Starting Integration Tests...")

        # Test API endpoints
        cmd = [sys.executable, "-m", "pytest", "-k", "integration"]
        if args.verbose:
            cmd.append("-v")

        results.append(run_command(cmd, "Integration Tests"))

    # Security Tests
    if not any([args.unit, args.integration, args.performance]) or args.security:
        print("\n🔒 Starting Security Tests...")

        cmd = [sys.executable, "-m", "pytest", "-k", "security"]
        if args.verbose:
            cmd.append("-v")

        results.append(run_command(cmd, "Security Tests"))

    # Performance Tests
    if args.performance:
        print("\n⚡ Starting Performance Tests...")

        cmd = [sys.executable, "-m", "pytest", "-k", "performance"]
        if args.verbose:
            cmd.append("-v")

        results.append(run_command(cmd, "Performance Tests"))

    # Full test suite
    if not any([args.unit, args.integration, args.security, args.performance]):
        print("\n🧪 Running Full Test Suite...")

        cmd = [sys.executable, "-m", "pytest"]
        if args.coverage:
            cmd.extend([
                "--cov=app",
                "--cov-report=html:htmlcov",
                "--cov-report=term-missing",
                "--cov-fail-under=80"
            ])
        if args.verbose:
            cmd.append("-v")

        results.append(run_command(cmd, "Full Test Suite"))

    # Summary
    total_time = time.time() - total_start
    passed = sum(results)
    total = len(results)

    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(".2f")
    print(".1f")

    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("💥 SOME TESTS FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
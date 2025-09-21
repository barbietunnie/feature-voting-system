#!/usr/bin/env python3
"""
Test runner script for the Feature Voting System backend.

This script sets up the proper environment variables and runs the test suite.
"""

import os
import sys
import subprocess

def setup_test_environment():
    """Set up environment variables for testing"""
    os.environ["TESTING"] = "true"
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"

def run_tests():
    """Run the test suite with proper configuration"""
    setup_test_environment()

    # Default pytest arguments
    pytest_args = [
        "python", "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--cov=app",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
    ]

    # Add any additional arguments passed to this script
    if len(sys.argv) > 1:
        pytest_args.extend(sys.argv[1:])

    try:
        result = subprocess.run(pytest_args, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\nTest run interrupted by user")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
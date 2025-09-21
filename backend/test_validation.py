#!/usr/bin/env python3
"""
Simple validation test script for Feature Voting System API
Run this script to test validation scenarios manually
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_feature_creation_validation():
    """Test feature creation with various validation scenarios"""
    print("Testing Feature Creation Validation...")

    # Test cases for feature creation
    test_cases = [
        {
            "name": "Valid feature",
            "data": {"title": "Valid Feature", "description": "This is a valid feature description"},
            "expected_status": 201
        },
        {
            "name": "Title too short",
            "data": {"title": "Hi", "description": "This is a valid feature description"},
            "expected_status": 422
        },
        {
            "name": "Title too long",
            "data": {"title": "a" * 101, "description": "This is a valid feature description"},
            "expected_status": 422
        },
        {
            "name": "Description too short",
            "data": {"title": "Valid Feature", "description": "Short"},
            "expected_status": 422
        },
        {
            "name": "Description too long",
            "data": {"title": "Valid Feature", "description": "a" * 1001},
            "expected_status": 422
        },
        {
            "name": "Empty title",
            "data": {"title": "", "description": "This is a valid feature description"},
            "expected_status": 422
        },
        {
            "name": "Whitespace only title",
            "data": {"title": "   ", "description": "This is a valid feature description"},
            "expected_status": 422
        },
        {
            "name": "Missing fields",
            "data": {"title": "Valid Feature"},
            "expected_status": 422
        }
    ]

    headers = {"X-User-ID": "1", "Content-Type": "application/json"}

    for test_case in test_cases:
        print(f"\n  Testing: {test_case['name']}")
        try:
            response = requests.post(
                f"{BASE_URL}/api/features/",
                headers=headers,
                json=test_case["data"]
            )
            status = response.status_code

            if status == test_case["expected_status"]:
                print(f"    ✓ PASS - Status: {status}")
            else:
                print(f"    ✗ FAIL - Expected: {test_case['expected_status']}, Got: {status}")
                print(f"    Response: {response.text}")

        except requests.exceptions.ConnectionError:
            print(f"    ⚠ SKIP - Server not running at {BASE_URL}")
            return

def test_pagination_validation():
    """Test pagination parameter validation"""
    print("\nTesting Pagination Validation...")

    test_cases = [
        {
            "name": "Valid pagination",
            "params": {"page": 1, "page_size": 20},
            "expected_status": 200
        },
        {
            "name": "Invalid page (zero)",
            "params": {"page": 0, "page_size": 20},
            "expected_status": 422
        },
        {
            "name": "Invalid page (negative)",
            "params": {"page": -1, "page_size": 20},
            "expected_status": 422
        },
        {
            "name": "Invalid page_size (zero)",
            "params": {"page": 1, "page_size": 0},
            "expected_status": 422
        },
        {
            "name": "Page size too large",
            "params": {"page": 1, "page_size": 101},
            "expected_status": 422
        }
    ]

    for test_case in test_cases:
        print(f"\n  Testing: {test_case['name']}")
        try:
            response = requests.get(
                f"{BASE_URL}/api/features/",
                params=test_case["params"]
            )
            status = response.status_code

            if status == test_case["expected_status"]:
                print(f"    ✓ PASS - Status: {status}")
            else:
                print(f"    ✗ FAIL - Expected: {test_case['expected_status']}, Got: {status}")
                print(f"    Response: {response.text}")

        except requests.exceptions.ConnectionError:
            print(f"    ⚠ SKIP - Server not running at {BASE_URL}")
            return

def test_vote_validation():
    """Test voting validation scenarios"""
    print("\nTesting Vote Validation...")

    headers = {"X-User-ID": "1"}

    # First, try to create a feature for testing
    try:
        feature_response = requests.post(
            f"{BASE_URL}/api/features/",
            headers={**headers, "Content-Type": "application/json"},
            json={"title": "Test Feature", "description": "Test feature for voting"}
        )

        if feature_response.status_code == 201:
            feature_id = feature_response.json()["id"]
            print(f"  Created test feature with ID: {feature_id}")
        else:
            print("  ⚠ Could not create test feature, using ID 1")
            feature_id = 1

    except requests.exceptions.ConnectionError:
        print(f"    ⚠ SKIP - Server not running at {BASE_URL}")
        return

    test_cases = [
        {
            "name": "Valid vote",
            "feature_id": feature_id,
            "expected_status": 201
        },
        {
            "name": "Duplicate vote",
            "feature_id": feature_id,
            "expected_status": 400
        },
        {
            "name": "Invalid feature ID (zero)",
            "feature_id": 0,
            "expected_status": 400
        },
        {
            "name": "Invalid feature ID (negative)",
            "feature_id": -1,
            "expected_status": 400
        },
        {
            "name": "Non-existent feature",
            "feature_id": 99999,
            "expected_status": 404
        }
    ]

    for test_case in test_cases:
        print(f"\n  Testing: {test_case['name']}")
        try:
            response = requests.post(
                f"{BASE_URL}/api/features/{test_case['feature_id']}/vote",
                headers=headers
            )
            status = response.status_code

            if status == test_case["expected_status"]:
                print(f"    ✓ PASS - Status: {status}")
            else:
                print(f"    ✗ FAIL - Expected: {test_case['expected_status']}, Got: {status}")
                print(f"    Response: {response.text}")

        except requests.exceptions.ConnectionError:
            print(f"    ⚠ SKIP - Server not running at {BASE_URL}")
            return

if __name__ == "__main__":
    print("=" * 50)
    print("Feature Voting System - Validation Tests")
    print("=" * 50)
    print(f"Testing API at: {BASE_URL}")
    print("Make sure the server is running with: uvicorn app.main:app --reload")
    print()

    test_feature_creation_validation()
    test_pagination_validation()
    test_vote_validation()

    print("\n" + "=" * 50)
    print("Validation testing complete!")
    print("=" * 50)
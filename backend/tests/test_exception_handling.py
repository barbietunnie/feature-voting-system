import pytest
from fastapi import status
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import IntegrityError, OperationalError, DatabaseError
from tests.factories import create_users_batch, create_features_batch

@pytest.mark.unit
class TestDatabaseExceptionHandling:
    """Test handling of database-related exceptions"""

    @patch('app.core.database.get_db')
    def test_database_connection_error(self, mock_get_db, client):
        """Test handling when database connection fails"""
        # Mock database session to raise connection error
        mock_session = MagicMock()
        mock_session.query.side_effect = OperationalError("Connection failed", None, None)
        mock_get_db.return_value = mock_session

        response = client.get("/api/users/")

        # Should return 500 Internal Server Error for database issues
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_integrity_constraint_violation_user(self, client, create_test_user):
        """Test handling of integrity constraint violations for users"""
        # Create a user
        user = create_test_user(username="duplicate", email="duplicate@example.com")

        # Try to create user with duplicate username
        duplicate_user_data = {
            "username": "duplicate",
            "email": "different@example.com"
        }
        response = client.post("/api/users/", json=duplicate_user_data)

        # Should handle constraint violation gracefully
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

        # Try to create user with duplicate email
        duplicate_email_data = {
            "username": "different",
            "email": "duplicate@example.com"
        }
        response = client.post("/api/users/", json=duplicate_email_data)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_foreign_key_constraint_violation(self, authenticated_client):
        """Test handling of foreign key constraint violations"""
        # Try to create feature with non-existent author_id
        # This is handled by authentication middleware, but test database constraint
        feature_data = {
            "title": "Invalid Author Feature",
            "description": "Feature with invalid author"
        }

        # Mock authentication to use non-existent user ID
        with patch('app.routes.features.get_current_user_id', return_value=999):
            response = authenticated_client.post("/api/features/", json=feature_data)

            # Should handle foreign key violation appropriately
            assert response.status_code in [
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                status.HTTP_404_NOT_FOUND
            ]

@pytest.mark.unit
class TestValidationExceptionHandling:
    """Test handling of validation exceptions"""

    def test_malformed_json_request(self, client):
        """Test handling of malformed JSON in requests"""
        # Send malformed JSON
        response = client.post(
            "/api/users/",
            data="{'invalid': json}",  # Invalid JSON
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_missing_content_type(self, client):
        """Test handling when Content-Type header is missing"""
        response = client.post(
            "/api/users/",
            data='{"username": "test", "email": "test@example.com"}'
            # No Content-Type header
        )

        # Should handle gracefully
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST
        ]

    def test_empty_request_body(self, client):
        """Test handling of empty request body"""
        response = client.post(
            "/api/users/",
            json={}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_null_values_in_required_fields(self, client):
        """Test handling of null values in required fields"""
        test_cases = [
            {"username": None, "email": "test@example.com"},
            {"username": "test", "email": None},
            {"username": None, "email": None},
        ]

        for test_data in test_cases:
            response = client.post("/api/users/", json=test_data)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_data_types(self, client):
        """Test handling of invalid data types"""
        test_cases = [
            {"username": 123, "email": "test@example.com"},  # username as number
            {"username": "test", "email": 456},  # email as number
            {"username": ["array"], "email": "test@example.com"},  # username as array
            {"username": "test", "email": {"object": "value"}},  # email as object
        ]

        for test_data in test_cases:
            response = client.post("/api/users/", json=test_data)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.unit
class TestAuthenticationExceptionHandling:
    """Test handling of authentication-related exceptions"""

    def test_missing_auth_header(self, client, create_test_feature):
        """Test handling when authentication header is missing"""
        feature = create_test_feature()

        # Try to vote without auth header
        response = client.post(f"/api/features/{feature.id}/vote")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Try to create feature without auth header
        feature_data = {"title": "Test", "description": "Test description"}
        response = client.post("/api/features/", json=feature_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_auth_header_format(self, client, create_test_feature):
        """Test handling of invalid authentication header formats"""
        feature = create_test_feature()

        invalid_headers = [
            {"X-User-ID": ""},  # Empty
            {"X-User-ID": "not-a-number"},  # Non-numeric
            {"X-User-ID": "-1"},  # Negative
            {"X-User-ID": "0"},  # Zero
            {"X-User-ID": "1.5"},  # Float
            {"X-User-ID": " 1 "},  # With spaces
        ]

        for headers in invalid_headers:
            response = client.post(f"/api/features/{feature.id}/vote", headers=headers)
            assert response.status_code in [
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ]

    def test_non_existent_user_auth(self, client, create_test_feature):
        """Test handling when authenticated user doesn't exist"""
        feature = create_test_feature()

        # Use ID of user that doesn't exist
        auth_headers = {"X-User-ID": "999999"}
        response = client.post(f"/api/features/{feature.id}/vote", headers=auth_headers)

        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_404_NOT_FOUND
        ]

@pytest.mark.unit
class TestResourceNotFoundHandling:
    """Test handling of resource not found scenarios"""

    def test_feature_not_found_endpoints(self, authenticated_client):
        """Test all endpoints that depend on feature existence"""
        non_existent_id = 999999

        # GET feature
        response = authenticated_client.get(f"/api/features/{non_existent_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # PUT feature
        update_data = {"title": "Updated"}
        response = authenticated_client.put(f"/api/features/{non_existent_id}", json=update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # POST vote
        response = authenticated_client.post(f"/api/features/{non_existent_id}/vote")
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # DELETE vote
        response = authenticated_client.delete(f"/api/features/{non_existent_id}/vote")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_user_not_found_endpoints(self, client):
        """Test endpoints that depend on user existence"""
        non_existent_id = 999999

        # GET user
        response = client.get(f"/api/users/{non_existent_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "User not found" in data["detail"]

    def test_vote_not_found_scenarios(self, authenticated_client, create_test_user, create_test_feature):
        """Test vote-related not found scenarios"""
        user = create_test_user()
        feature = create_test_feature(author_id=user.id)

        # Try to unvote when no vote exists
        response = authenticated_client.delete(f"/api/features/{feature.id}/vote")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "not voted" in data["detail"].lower()

@pytest.mark.unit
class TestInvalidParameterHandling:
    """Test handling of invalid URL parameters"""

    def test_invalid_id_parameters(self, client):
        """Test handling of invalid ID parameters in URLs"""
        invalid_ids = [
            "abc",  # Non-numeric
            "-1",   # Negative
            "0",    # Zero
            "1.5",  # Float
            "999999999999999999999",  # Very large number
            "",     # Empty
            " ",    # Space
            "null", # String null
        ]

        endpoints = [
            "/api/users/{}",
            "/api/features/{}",
            "/api/features/{}/vote",
        ]

        for endpoint_template in endpoints:
            for invalid_id in invalid_ids:
                endpoint = endpoint_template.format(invalid_id)
                response = client.get(endpoint)

                # Should return validation error
                assert response.status_code in [
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    status.HTTP_400_BAD_REQUEST,
                    status.HTTP_404_NOT_FOUND
                ]

    def test_invalid_pagination_parameters(self, client):
        """Test handling of invalid pagination parameters"""
        invalid_params = [
            "page=-1",
            "page=0",
            "page=abc",
            "page_size=-1",
            "page_size=0",
            "page_size=101",  # Over limit
            "page_size=abc",
            "limit=-1",
            "limit=abc",
            "skip=-1",
            "skip=abc",
        ]

        for param in invalid_params:
            response = client.get(f"/api/features/?{param}")
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.integration
class TestConcurrentExceptionHandling:
    """Test exception handling under concurrent operations"""

    def test_concurrent_constraint_violations(self, client, db_session, create_test_user, create_test_feature):
        """Test handling of concurrent constraint violations"""
        import threading

        user = create_test_user()
        feature = create_test_feature(author_id=user.id)
        auth_headers = {"X-User-ID": str(user.id)}

        results = []

        def attempt_duplicate_vote():
            try:
                response = client.post(f"/api/features/{feature.id}/vote", headers=auth_headers)
                results.append(response.status_code)
            except Exception as e:
                results.append(f"Exception: {str(e)}")

        # Try to create duplicate votes concurrently
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=attempt_duplicate_vote)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Only one should succeed, others should fail gracefully
        success_count = results.count(status.HTTP_200_OK)
        error_count = results.count(status.HTTP_400_BAD_REQUEST)

        assert success_count == 1
        assert error_count == 4
        assert all(isinstance(result, int) for result in results)  # No unhandled exceptions

    def test_concurrent_resource_access(self, client, db_session):
        """Test concurrent access to resources with some operations failing"""
        import threading
        import random

        # Create test data
        users = create_users_batch(db_session, count=3)
        features = create_features_batch(db_session, count=2, author_id=users[0].id)

        results = []

        def mixed_operations():
            """Perform mix of valid and invalid operations"""
            operations = [
                # Valid operations
                lambda: client.get("/api/features/"),
                lambda: client.get(f"/api/features/{features[0].id}"),
                lambda: client.post(f"/api/features/{features[0].id}/vote",
                                  headers={"X-User-ID": str(users[1].id)}),

                # Invalid operations
                lambda: client.get("/api/features/999"),  # Non-existent feature
                lambda: client.post("/api/features/999/vote",
                                  headers={"X-User-ID": str(users[1].id)}),  # Non-existent feature
                lambda: client.post(f"/api/features/{features[0].id}/vote",
                                  headers={"X-User-ID": "999"}),  # Non-existent user
            ]

            operation = random.choice(operations)
            try:
                response = operation()
                results.append(response.status_code)
            except Exception as e:
                results.append(f"Exception: {str(e)}")

        # Run concurrent mixed operations
        threads = []
        for _ in range(20):
            thread = threading.Thread(target=mixed_operations)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Verify all operations completed without unhandled exceptions
        assert len(results) == 20
        assert all(isinstance(result, int) for result in results)  # No unhandled exceptions

        # Should have mix of success and error status codes
        success_codes = [r for r in results if 200 <= r < 300]
        error_codes = [r for r in results if 400 <= r < 600]

        assert len(success_codes) > 0
        assert len(error_codes) > 0

@pytest.mark.edge_case
class TestExtremeInputHandling:
    """Test handling of extreme inputs and edge cases"""

    def test_extremely_large_payloads(self, client):
        """Test handling of very large request payloads"""
        # Create very large payload
        large_string = "a" * 100000  # 100KB string

        large_payload = {
            "username": large_string,
            "email": f"{large_string}@example.com"
        }

        response = client.post("/api/users/", json=large_payload)

        # Should handle gracefully with validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_deeply_nested_json(self, client):
        """Test handling of deeply nested JSON structures"""
        # Create deeply nested structure
        nested_data = {"username": "test", "email": "test@example.com"}
        for i in range(100):  # Create 100 levels of nesting
            nested_data = {"data": nested_data}

        response = client.post("/api/users/", json=nested_data)

        # Should handle gracefully
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_special_unicode_characters(self, client):
        """Test handling of special Unicode characters"""
        special_chars = [
            "\u0000",  # Null character
            "\uFFFE",  # Non-character
            "\uFFFF",  # Non-character
            "\U0001F4A9",  # Emoji
            "🚀" * 1000,  # Many emojis
            "\n" * 1000,  # Many newlines
            "\t" * 1000,  # Many tabs
        ]

        for special_char in special_chars:
            user_data = {
                "username": f"test{special_char}",
                "email": "test@example.com"
            }

            response = client.post("/api/users/", json=user_data)

            # Should either succeed or fail gracefully
            assert response.status_code in [
                status.HTTP_201_CREATED,
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                status.HTTP_400_BAD_REQUEST
            ]

    def test_memory_exhaustion_protection(self, client):
        """Test protection against memory exhaustion attacks"""
        # Try to create many large objects rapidly
        for _ in range(10):
            large_data = {
                "username": "a" * 10000,
                "email": "test@example.com"
            }

            response = client.post("/api/users/", json=large_data)

            # Should handle without crashing
            assert response.status_code in [
                status.HTTP_201_CREATED,
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ]

@pytest.mark.integration
class TestErrorRecoveryAndResilience:
    """Test system recovery and resilience after errors"""

    def test_system_recovery_after_errors(self, client, db_session):
        """Test that system continues to work after encountering errors"""
        # Create valid data
        user_data = {"username": "recovery_user", "email": "recovery@example.com"}
        response = client.post("/api/users/", json=user_data)
        assert response.status_code == status.HTTP_201_CREATED
        user = response.json()

        # Cause some errors
        invalid_requests = [
            ("/api/users/", {"username": "", "email": "invalid"}),  # Invalid user
            ("/api/features/999", {}),  # Non-existent feature
            ("/api/users/abc", {}),  # Invalid ID format
        ]

        for endpoint, data in invalid_requests:
            if data:
                response = client.post(endpoint, json=data)
            else:
                response = client.get(endpoint)
            # Expect errors
            assert response.status_code >= 400

        # System should still work for valid requests
        auth_headers = {"X-User-ID": str(user["id"])}
        feature_data = {
            "title": "Recovery Test Feature",
            "description": "Testing system recovery after errors"
        }

        response = client.post("/api/features/", json=feature_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED

        # List features should still work
        response = client.get("/api/features/")
        assert response.status_code == status.HTTP_200_OK

    def test_partial_failure_handling(self, client, db_session):
        """Test handling when some operations succeed and others fail"""
        # Create users
        users = create_users_batch(db_session, count=3)
        feature = create_features_batch(db_session, count=1, author_id=users[0].id)[0]

        # Mix of valid and invalid vote attempts
        vote_attempts = [
            (users[1].id, True),   # Valid user
            (users[2].id, True),   # Valid user
            (999, False),          # Invalid user
            (users[1].id, False),  # Duplicate vote
        ]

        successful_votes = 0
        for user_id, should_succeed in vote_attempts:
            auth_headers = {"X-User-ID": str(user_id)}
            response = client.post(f"/api/features/{feature.id}/vote", headers=auth_headers)

            if should_succeed and response.status_code == status.HTTP_200_OK:
                successful_votes += 1

        # Verify partial success
        assert successful_votes == 2

        # System should still be consistent
        response = client.get(f"/api/features/{feature.id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["vote_count"] == successful_votes
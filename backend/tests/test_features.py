import pytest
from fastapi import status
from tests.factories import TestDataGenerator, create_features_batch, create_users_batch

@pytest.mark.unit
@pytest.mark.auth
class TestFeatureCreation:
    """Test feature creation endpoint"""

    def test_create_feature_valid_data(self, authenticated_client, create_test_user, sample_feature_data):
        """Test creating a feature with valid data and authentication"""
        # Create user first
        user = create_test_user(username="author", email="author@example.com")

        response = authenticated_client.post("/api/features/", json=sample_feature_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == sample_feature_data["title"]
        assert data["description"] == sample_feature_data["description"]
        assert data["author_id"] == 1  # From auth header
        assert data["vote_count"] == 0
        assert "id" in data
        assert "created_at" in data

    def test_create_feature_without_auth(self, client, sample_feature_data):
        """Test creating feature without authentication"""
        response = client.post("/api/features/", json=sample_feature_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "X-User-ID header is required" in data["detail"]

    def test_create_feature_invalid_user_id(self, client, sample_feature_data):
        """Test creating feature with invalid user ID in header"""
        invalid_headers = [
            {"X-User-ID": "invalid"},
            {"X-User-ID": "-1"},
            {"X-User-ID": "0"},
            {"X-User-ID": ""},
        ]

        for headers in invalid_headers:
            response = client.post("/api/features/", json=sample_feature_data, headers=headers)
            assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED]

    @pytest.mark.parametrize("invalid_data", TestDataGenerator.invalid_feature_data())
    def test_create_feature_invalid_data(self, authenticated_client, invalid_data):
        """Test creating feature with various invalid data"""
        response = authenticated_client.post("/api/features/", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_feature_boundary_values(self, authenticated_client):
        """Test feature creation with boundary values"""
        boundary_data = TestDataGenerator.boundary_test_data()

        # Test minimum valid values
        valid_min_data = {
            "title": boundary_data["title_min"],
            "description": boundary_data["desc_min"]
        }
        response = authenticated_client.post("/api/features/", json=valid_min_data)
        assert response.status_code == status.HTTP_201_CREATED

        # Test maximum valid values
        valid_max_data = {
            "title": boundary_data["title_max"],
            "description": boundary_data["desc_max"]
        }
        response = authenticated_client.post("/api/features/", json=valid_max_data)
        assert response.status_code == status.HTTP_201_CREATED

        # Test over maximum (should fail)
        invalid_over_data = {
            "title": boundary_data["title_over"],
            "description": boundary_data["desc_over"]
        }
        response = authenticated_client.post("/api/features/", json=invalid_over_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test under minimum (should fail)
        invalid_under_data = {
            "title": boundary_data["title_under"],
            "description": boundary_data["desc_under"]
        }
        response = authenticated_client.post("/api/features/", json=invalid_under_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.unit
class TestFeatureRetrieval:
    """Test feature retrieval endpoints"""

    def test_get_features_empty(self, client):
        """Test getting features when database is empty"""
        response = client.get("/api/features/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["items"] == []
        assert data["total_count"] == 0
        assert data["page"] == 1
        assert data["page_size"] == 20

    def test_get_features_with_data(self, client, db_session, create_test_user):
        """Test getting features when data exists"""
        # Create user and features
        user = create_test_user()
        features = create_features_batch(db_session, count=5, author_id=user.id)

        response = client.get("/api/features/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 5
        assert data["total_count"] == 5

    def test_get_features_sorted_by_votes(self, client, db_session, create_test_user):
        """Test that features are returned sorted by vote count (descending)"""
        user = create_test_user()

        # Create features with different vote counts
        feature1 = create_features_batch(db_session, count=1, author_id=user.id)[0]
        feature1.vote_count = 5
        feature2 = create_features_batch(db_session, count=1, author_id=user.id)[0]
        feature2.vote_count = 10
        feature3 = create_features_batch(db_session, count=1, author_id=user.id)[0]
        feature3.vote_count = 1

        db_session.commit()

        response = client.get("/api/features/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items = data["items"]

        # Should be sorted by vote_count descending
        assert items[0]["vote_count"] == 10
        assert items[1]["vote_count"] == 5
        assert items[2]["vote_count"] == 1

    def test_get_features_pagination(self, client, db_session, create_test_user):
        """Test feature pagination"""
        user = create_test_user()
        create_features_batch(db_session, count=25, author_id=user.id)

        # Test first page
        response = client.get("/api/features/?page=1&page_size=10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 10
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total_count"] == 25
        assert data["total_pages"] == 3
        assert data["has_next"] is True
        assert data["has_previous"] is False

        # Test second page
        response = client.get("/api/features/?page=2&page_size=10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 10
        assert data["page"] == 2
        assert data["has_next"] is True
        assert data["has_previous"] is True

        # Test last page
        response = client.get("/api/features/?page=3&page_size=10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 5  # Remaining items
        assert data["page"] == 3
        assert data["has_next"] is False
        assert data["has_previous"] is True

    def test_get_features_pagination_invalid_params(self, client):
        """Test feature pagination with invalid parameters"""
        invalid_params = [
            "page=0",  # Page too low
            "page=-1",  # Negative page
            "page_size=0",  # Page size too low
            "page_size=101",  # Page size too high
            "page=abc",  # Invalid page format
            "page_size=xyz",  # Invalid page size format
        ]

        for param in invalid_params:
            response = client.get(f"/api/features/?{param}")
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_single_feature(self, client, create_test_user, create_test_feature):
        """Test getting a single feature by ID"""
        user = create_test_user()
        feature = create_test_feature(author_id=user.id)

        response = client.get(f"/api/features/{feature.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == feature.id
        assert data["title"] == feature.title
        assert data["description"] == feature.description
        assert data["author_id"] == user.id

    def test_get_single_feature_not_found(self, client):
        """Test getting a feature that doesn't exist"""
        response = client.get("/api/features/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.unit
class TestFeatureUpdate:
    """Test feature update endpoint"""

    def test_update_feature_valid_data(self, authenticated_client, create_test_user, create_test_feature):
        """Test updating a feature with valid data"""
        user = create_test_user()
        feature = create_test_feature(author_id=user.id)

        update_data = {
            "title": "Updated Title",
            "description": "Updated description that is long enough"
        }

        response = authenticated_client.put(f"/api/features/{feature.id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]
        assert data["id"] == feature.id

    def test_update_feature_partial(self, authenticated_client, create_test_user, create_test_feature):
        """Test partial update of a feature"""
        user = create_test_user()
        feature = create_test_feature(title="Original Title", author_id=user.id)

        # Update only title
        update_data = {"title": "New Title"}
        response = authenticated_client.put(f"/api/features/{feature.id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "New Title"
        assert data["description"] == feature.description  # Should remain unchanged

    def test_update_feature_not_found(self, authenticated_client):
        """Test updating a feature that doesn't exist"""
        update_data = {"title": "New Title"}
        response = authenticated_client.put("/api/features/999", json=update_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_feature_invalid_id(self, authenticated_client):
        """Test updating feature with invalid ID"""
        update_data = {"title": "New Title"}

        invalid_ids = [-1, 0, "abc"]
        for invalid_id in invalid_ids:
            response = authenticated_client.put(f"/api/features/{invalid_id}", json=update_data)
            assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]

@pytest.mark.validation
class TestFeatureValidation:
    """Test feature data validation"""

    def test_title_whitespace_handling(self, authenticated_client):
        """Test handling of whitespace in titles"""
        test_cases = [
            ("  Valid Title  ", "Valid Title"),  # Should trim whitespace
            ("Valid\tTitle", "Valid\tTitle"),    # Internal whitespace preserved
            ("Valid\nTitle", "Valid\nTitle"),    # Newlines
        ]

        for input_title, expected_title in test_cases:
            feature_data = {
                "title": input_title,
                "description": "Valid description that is long enough"
            }

            response = authenticated_client.post("/api/features/", json=feature_data)
            if response.status_code == status.HTTP_201_CREATED:
                data = response.json()
                assert data["title"] == expected_title

    def test_description_whitespace_handling(self, authenticated_client):
        """Test handling of whitespace in descriptions"""
        test_cases = [
            ("  Valid description that is long enough  ", "Valid description that is long enough"),
            ("Valid\tdescription\tthat\tis\tlong\tenough", "Valid\tdescription\tthat\tis\tlong\tenough"),
        ]

        for input_desc, expected_desc in test_cases:
            feature_data = {
                "title": "Valid Title",
                "description": input_desc
            }

            response = authenticated_client.post("/api/features/", json=feature_data)
            if response.status_code == status.HTTP_201_CREATED:
                data = response.json()
                assert data["description"] == expected_desc

    def test_special_characters_in_content(self, authenticated_client):
        """Test handling of special characters in feature content"""
        special_chars_data = {
            "title": "Feature with special chars: !@#$%^&*()",
            "description": "Description with émojis 🚀 and spëcial characters áéíóú"
        }

        response = authenticated_client.post("/api/features/", json=special_chars_data)
        assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.edge_case
class TestFeatureEdgeCases:
    """Test edge cases and error conditions for features"""

    def test_sql_injection_in_feature_data(self, authenticated_client):
        """Test SQL injection attempts in feature data"""
        malicious_data = {
            "title": "Feature'; DROP TABLE features; --",
            "description": "Malicious description with SQL injection attempt"
        }

        response = authenticated_client.post("/api/features/", json=malicious_data)
        # Should either create safely or reject
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]

        # Verify features table still works
        get_response = authenticated_client.get("/api/features/")
        assert get_response.status_code == status.HTTP_200_OK

    def test_xss_in_feature_data(self, authenticated_client):
        """Test XSS attempts in feature data"""
        xss_data = {
            "title": "<script>alert('xss')</script>",
            "description": "<img src=x onerror=alert('xss')> malicious description"
        }

        response = authenticated_client.post("/api/features/", json=xss_data)
        # Should either create safely or reject
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_unicode_in_feature_data(self, authenticated_client):
        """Test unicode characters in feature data"""
        unicode_data = {
            "title": "功能标题 with émojis 🚀",
            "description": "Description with various unicode: 你好世界 café naïve résumé"
        }

        response = authenticated_client.post("/api/features/", json=unicode_data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_null_bytes_in_feature_data(self, authenticated_client):
        """Test handling of null bytes in feature data"""
        null_data = {
            "title": "Title\x00with\x00nulls",
            "description": "Description\x00with\x00null\x00bytes\x00that\x00is\x00long\x00enough"
        }

        response = authenticated_client.post("/api/features/", json=null_data)
        # Should handle gracefully
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_concurrent_feature_creation(self, client, db_session, create_test_user):
        """Test concurrent feature creation by same user"""
        import threading
        import time

        user = create_test_user()
        auth_headers = {"X-User-ID": str(user.id)}

        results = []

        def create_feature(index):
            feature_data = {
                "title": f"Concurrent Feature {index}",
                "description": f"Description for concurrent feature {index} that is long enough"
            }
            response = client.post("/api/features/", json=feature_data, headers=auth_headers)
            results.append(response.status_code)

        # Create multiple features concurrently
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_feature, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # All should succeed
        assert all(status_code == status.HTTP_201_CREATED for status_code in results)
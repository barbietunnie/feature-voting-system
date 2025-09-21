import pytest
from fastapi import status
from tests.factories import TestDataGenerator, create_users_batch

@pytest.mark.unit
class TestUserCreation:
    """Test user creation endpoint"""

    def test_create_user_valid_data(self, client, sample_user_data):
        """Test creating a user with valid data"""
        response = client.post("/api/users/", json=sample_user_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == sample_user_data["username"]
        assert data["email"] == sample_user_data["email"]
        assert "id" in data
        assert "created_at" in data

    def test_create_user_duplicate_username(self, client, db_session, create_test_user):
        """Test creating user with duplicate username"""
        # Create first user
        create_test_user(username="duplicate", email="first@example.com")

        # Try to create second user with same username
        user_data = {"username": "duplicate", "email": "second@example.com"}
        response = client.post("/api/users/", json=user_data)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_create_user_duplicate_email(self, client, db_session, create_test_user):
        """Test creating user with duplicate email"""
        # Create first user
        create_test_user(username="first", email="duplicate@example.com")

        # Try to create second user with same email
        user_data = {"username": "second", "email": "duplicate@example.com"}
        response = client.post("/api/users/", json=user_data)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    @pytest.mark.parametrize("invalid_data", TestDataGenerator.invalid_user_data())
    def test_create_user_invalid_data(self, client, invalid_data):
        """Test creating user with various invalid data"""
        response = client.post("/api/users/", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_user_missing_fields(self, client):
        """Test creating user with missing required fields"""
        test_cases = [
            {},  # No fields
            {"username": "test"},  # Missing email
            {"email": "test@example.com"},  # Missing username
        ]

        for invalid_data in test_cases:
            response = client.post("/api/users/", json=invalid_data)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.unit
class TestUserRetrieval:
    """Test user retrieval endpoints"""

    def test_get_all_users_empty(self, client):
        """Test getting users when database is empty"""
        response = client.get("/api/users/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == []

    def test_get_all_users_with_data(self, client, db_session):
        """Test getting all users when data exists"""
        # Create test users
        users = create_users_batch(db_session, count=3)

        response = client.get("/api/users/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3

        # Verify user data
        for i, user_data in enumerate(data):
            assert user_data["username"] == f"testuser{i}"
            assert user_data["email"] == f"test{i}@example.com"

    def test_get_users_pagination(self, client, db_session):
        """Test user pagination"""
        # Create many users
        create_users_batch(db_session, count=10)

        # Test with limit
        response = client.get("/api/users/?limit=5")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 5

        # Test with skip and limit
        response = client.get("/api/users/?skip=5&limit=3")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3

    def test_get_user_by_id_exists(self, client, create_test_user):
        """Test getting user by ID when user exists"""
        user = create_test_user(username="testuser", email="test@example.com")

        response = client.get(f"/api/users/{user.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == user.id
        assert data["username"] == user.username
        assert data["email"] == user.email

    def test_get_user_by_id_not_found(self, client):
        """Test getting user by ID when user doesn't exist"""
        response = client.get("/api/users/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "User not found" in data["detail"]

    @pytest.mark.parametrize("invalid_id", [-1, 0, "abc", ""])
    def test_get_user_invalid_id(self, client, invalid_id):
        """Test getting user with invalid ID format"""
        response = client.get(f"/api/users/{invalid_id}")

        # Should return 422 for invalid format or 404 for negative numbers
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_404_NOT_FOUND]

@pytest.mark.validation
class TestUserValidation:
    """Test user data validation"""

    def test_username_edge_cases(self, client):
        """Test username with edge case values"""
        edge_cases = [
            ("", status.HTTP_422_UNPROCESSABLE_ENTITY),  # Empty
            ("   ", status.HTTP_422_UNPROCESSABLE_ENTITY),  # Whitespace only
            ("a", status.HTTP_201_CREATED),  # Single character (if allowed)
            ("a" * 100, status.HTTP_201_CREATED),  # Long username
        ]

        for username, expected_status in edge_cases:
            user_data = {"username": username, "email": "test@example.com"}
            response = client.post("/api/users/", json=user_data)
            assert response.status_code == expected_status

    def test_email_validation(self, client):
        """Test email format validation"""
        test_cases = [
            ("valid@example.com", status.HTTP_201_CREATED),
            ("user+tag@example.com", status.HTTP_201_CREATED),
            ("user.name@example.co.uk", status.HTTP_201_CREATED),
            ("invalid-email", status.HTTP_422_UNPROCESSABLE_ENTITY),
            ("@example.com", status.HTTP_422_UNPROCESSABLE_ENTITY),
            ("user@", status.HTTP_422_UNPROCESSABLE_ENTITY),
            ("", status.HTTP_422_UNPROCESSABLE_ENTITY),
        ]

        for email, expected_status in test_cases:
            user_data = {"username": "testuser", "email": email}
            response = client.post("/api/users/", json=user_data)
            assert response.status_code == expected_status

    def test_special_characters_in_username(self, client):
        """Test username with special characters"""
        special_usernames = [
            "user_name",  # Underscore
            "user-name",  # Hyphen
            "user123",    # Numbers
            "User",       # Uppercase
            "user.name",  # Dot
            "user@name",  # At symbol (might be invalid)
            "user name",  # Space (likely invalid)
        ]

        for username in special_usernames:
            user_data = {"username": username, "email": f"{username.replace(' ', '')}@example.com"}
            response = client.post("/api/users/", json=user_data)
            # Accept either success or validation error depending on validation rules
            assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_unicode_characters(self, client):
        """Test handling of unicode characters"""
        unicode_data = {
            "username": "用户名",  # Chinese characters
            "email": "test@example.com"
        }

        response = client.post("/api/users/", json=unicode_data)
        # Should either accept unicode or return validation error
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]

@pytest.mark.edge_case
class TestUserEdgeCases:
    """Test edge cases and error conditions"""

    def test_sql_injection_attempt(self, client):
        """Test SQL injection in user data"""
        malicious_data = {
            "username": "admin'; DROP TABLE users; --",
            "email": "hacker@example.com"
        }

        response = client.post("/api/users/", json=malicious_data)
        # Should either create user safely or reject input
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]

        # Verify users table still exists by trying to get users
        get_response = client.get("/api/users/")
        assert get_response.status_code == status.HTTP_200_OK

    def test_xss_attempt_in_user_data(self, client):
        """Test XSS attempt in user data"""
        xss_data = {
            "username": "<script>alert('xss')</script>",
            "email": "test@example.com"
        }

        response = client.post("/api/users/", json=xss_data)
        # Should either create user safely or reject input
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_very_long_input(self, client):
        """Test handling of extremely long input"""
        long_string = "a" * 10000

        long_data = {
            "username": long_string,
            "email": f"{long_string}@example.com"
        }

        response = client.post("/api/users/", json=long_data)
        # Should reject very long input
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_null_bytes_in_input(self, client):
        """Test handling of null bytes in input"""
        null_data = {
            "username": "user\x00name",
            "email": "test\x00@example.com"
        }

        response = client.post("/api/users/", json=null_data)
        # Should handle null bytes gracefully
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]
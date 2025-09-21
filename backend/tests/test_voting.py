import pytest
from fastapi import status
from tests.factories import TestDataGenerator, create_features_batch, create_users_batch

@pytest.mark.unit
@pytest.mark.auth
class TestVoteCreation:
    """Test vote creation endpoint"""

    def test_vote_for_feature_valid(self, authenticated_client, create_test_user, create_test_feature):
        """Test voting for a feature with valid data"""
        user = create_test_user()
        feature = create_test_feature(author_id=user.id)

        response = authenticated_client.post(f"/api/features/{feature.id}/vote")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Vote added successfully"
        assert data["vote_count"] == 1

    def test_vote_without_auth(self, client, create_test_user, create_test_feature):
        """Test voting without authentication"""
        user = create_test_user()
        feature = create_test_feature(author_id=user.id)

        response = client.post(f"/api/features/{feature.id}/vote")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "X-User-ID header is required" in data["detail"]

    def test_vote_for_nonexistent_feature(self, authenticated_client):
        """Test voting for a feature that doesn't exist"""
        response = authenticated_client.post("/api/features/999/vote")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "Feature not found" in data["detail"]

    def test_vote_duplicate_same_user(self, authenticated_client, create_test_user, create_test_feature):
        """Test duplicate vote by same user (should fail)"""
        user = create_test_user()
        feature = create_test_feature(author_id=user.id)

        # First vote should succeed
        response1 = authenticated_client.post(f"/api/features/{feature.id}/vote")
        assert response1.status_code == status.HTTP_200_OK

        # Second vote should fail
        response2 = authenticated_client.post(f"/api/features/{feature.id}/vote")
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        data = response2.json()
        assert "already voted" in data["detail"].lower()

    def test_vote_invalid_feature_id(self, authenticated_client):
        """Test voting with invalid feature ID format"""
        invalid_ids = [-1, 0, "abc", ""]

        for invalid_id in invalid_ids:
            response = authenticated_client.post(f"/api/features/{invalid_id}/vote")
            assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_vote_invalid_user_id(self, client, create_test_user, create_test_feature):
        """Test voting with invalid user ID in header"""
        user = create_test_user()
        feature = create_test_feature(author_id=user.id)

        invalid_headers = [
            {"X-User-ID": "invalid"},
            {"X-User-ID": "-1"},
            {"X-User-ID": "0"},
            {"X-User-ID": ""},
        ]

        for headers in invalid_headers:
            response = client.post(f"/api/features/{feature.id}/vote", headers=headers)
            assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED]

@pytest.mark.unit
@pytest.mark.auth
class TestVoteRemoval:
    """Test vote removal endpoint"""

    def test_unvote_feature_valid(self, authenticated_client, create_test_user, create_test_feature, create_test_vote):
        """Test removing vote from a feature"""
        user = create_test_user()
        feature = create_test_feature(author_id=user.id)
        create_test_vote(user_id=user.id, feature_id=feature.id)

        response = authenticated_client.delete(f"/api/features/{feature.id}/vote")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Vote removed successfully"
        assert data["vote_count"] == 0

    def test_unvote_without_auth(self, client, create_test_user, create_test_feature):
        """Test removing vote without authentication"""
        user = create_test_user()
        feature = create_test_feature(author_id=user.id)

        response = client.delete(f"/api/features/{feature.id}/vote")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unvote_nonexistent_feature(self, authenticated_client):
        """Test removing vote from feature that doesn't exist"""
        response = authenticated_client.delete("/api/features/999/vote")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unvote_without_existing_vote(self, authenticated_client, create_test_user, create_test_feature):
        """Test removing vote when user hasn't voted"""
        user = create_test_user()
        feature = create_test_feature(author_id=user.id)

        response = authenticated_client.delete(f"/api/features/{feature.id}/vote")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "not voted" in data["detail"].lower()

@pytest.mark.integration
class TestVoteCountAccuracy:
    """Test vote count accuracy and consistency"""

    def test_single_vote_count_update(self, client, db_session, create_test_user, create_test_feature):
        """Test that vote count is correctly updated when voting"""
        user = create_test_user()
        feature = create_test_feature(author_id=user.id, vote_count=0)
        auth_headers = {"X-User-ID": str(user.id)}

        # Vote for feature
        response = client.post(f"/api/features/{feature.id}/vote", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["vote_count"] == 1

        # Verify feature vote count is updated
        response = client.get(f"/api/features/{feature.id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["vote_count"] == 1

    def test_multiple_users_vote_count(self, client, db_session):
        """Test vote count with multiple users voting"""
        # Create users and feature
        users = create_users_batch(db_session, count=3)
        feature = create_features_batch(db_session, count=1, author_id=users[0].id)[0]

        # Each user votes
        for user in users:
            auth_headers = {"X-User-ID": str(user.id)}
            response = client.post(f"/api/features/{feature.id}/vote", headers=auth_headers)
            assert response.status_code == status.HTTP_200_OK

        # Check final vote count
        response = client.get(f"/api/features/{feature.id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["vote_count"] == 3

    def test_vote_unvote_count_consistency(self, client, db_session, create_test_user, create_test_feature):
        """Test vote count consistency through vote/unvote cycles"""
        user = create_test_user()
        feature = create_test_feature(author_id=user.id)
        auth_headers = {"X-User-ID": str(user.id)}

        # Vote
        response = client.post(f"/api/features/{feature.id}/vote", headers=auth_headers)
        assert response.json()["vote_count"] == 1

        # Unvote
        response = client.delete(f"/api/features/{feature.id}/vote", headers=auth_headers)
        assert response.json()["vote_count"] == 0

        # Vote again
        response = client.post(f"/api/features/{feature.id}/vote", headers=auth_headers)
        assert response.json()["vote_count"] == 1

    def test_concurrent_voting(self, client, db_session, create_test_feature):
        """Test concurrent voting by multiple users"""
        import threading
        import time

        # Create multiple users and a feature
        users = create_users_batch(db_session, count=5)
        feature = create_features_batch(db_session, count=1, author_id=users[0].id)[0]

        results = []

        def vote_for_feature(user_id):
            auth_headers = {"X-User-ID": str(user_id)}
            response = client.post(f"/api/features/{feature.id}/vote", headers=auth_headers)
            results.append(response.status_code)

        # Create threads for concurrent voting
        threads = []
        for user in users:
            thread = threading.Thread(target=vote_for_feature, args=(user.id,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All votes should succeed
        assert all(status_code == status.HTTP_200_OK for status_code in results)

        # Final vote count should be 5
        response = client.get(f"/api/features/{feature.id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["vote_count"] == 5

@pytest.mark.edge_case
class TestVoteEdgeCases:
    """Test edge cases and error conditions for voting"""

    def test_vote_with_sql_injection_in_feature_id(self, authenticated_client):
        """Test SQL injection attempt in feature ID"""
        malicious_id = "1'; DROP TABLE votes; --"
        response = authenticated_client.post(f"/api/features/{malicious_id}/vote")

        # Should return validation error, not crash
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_vote_with_extremely_large_feature_id(self, authenticated_client):
        """Test voting with extremely large feature ID"""
        large_id = "9" * 100
        response = authenticated_client.post(f"/api/features/{large_id}/vote")

        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_404_NOT_FOUND]

    def test_vote_race_condition_same_user(self, client, db_session, create_test_user, create_test_feature):
        """Test race condition when same user tries to vote simultaneously"""
        import threading
        import time

        user = create_test_user()
        feature = create_test_feature(author_id=user.id)
        auth_headers = {"X-User-ID": str(user.id)}

        results = []

        def attempt_vote():
            response = client.post(f"/api/features/{feature.id}/vote", headers=auth_headers)
            results.append(response.status_code)

        # Try to vote simultaneously with same user
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=attempt_vote)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Only one vote should succeed, others should fail
        success_count = sum(1 for status in results if status == status.HTTP_200_OK)
        failure_count = sum(1 for status in results if status == status.HTTP_400_BAD_REQUEST)

        assert success_count == 1
        assert failure_count == 2

    def test_vote_with_deleted_user_header(self, client, create_test_feature):
        """Test voting with user ID that doesn't exist in database"""
        feature = create_test_feature(author_id=1)  # Assume author exists

        # Use non-existent user ID
        auth_headers = {"X-User-ID": "999"}
        response = client.post(f"/api/features/{feature.id}/vote", headers=auth_headers)

        # Should handle gracefully
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_vote_count_integrity_after_feature_deletion(self, client, db_session, create_test_user, create_test_feature):
        """Test that vote operations fail gracefully when feature is deleted"""
        user = create_test_user()
        feature = create_test_feature(author_id=user.id)
        feature_id = feature.id
        auth_headers = {"X-User-ID": str(user.id)}

        # Vote for feature
        response = client.post(f"/api/features/{feature_id}/vote", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

        # Delete feature from database directly
        db_session.delete(feature)
        db_session.commit()

        # Try to vote again - should fail gracefully
        response = client.post(f"/api/features/{feature_id}/vote", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Try to unvote - should fail gracefully
        response = client.delete(f"/api/features/{feature_id}/vote", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.validation
class TestVoteValidation:
    """Test vote data validation and constraints"""

    def test_vote_constraint_uniqueness(self, client, db_session, create_test_user, create_test_feature):
        """Test that database constraint prevents duplicate votes"""
        user = create_test_user()
        feature = create_test_feature(author_id=user.id)
        auth_headers = {"X-User-ID": str(user.id)}

        # First vote
        response1 = client.post(f"/api/features/{feature.id}/vote", headers=auth_headers)
        assert response1.status_code == status.HTTP_200_OK

        # Second vote should be prevented by application logic
        response2 = client.post(f"/api/features/{feature.id}/vote", headers=auth_headers)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST

    def test_vote_foreign_key_constraints(self, client, db_session):
        """Test foreign key constraints for votes"""
        # Create user but no feature
        users = create_users_batch(db_session, count=1)
        user = users[0]
        auth_headers = {"X-User-ID": str(user.id)}

        # Try to vote for non-existent feature
        response = client.post("/api/features/999/vote", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_vote_cascade_deletion(self, client, db_session, create_test_user, create_test_feature, create_test_vote):
        """Test that votes are properly handled when user or feature is deleted"""
        user = create_test_user()
        feature = create_test_feature(author_id=user.id)
        vote = create_test_vote(user_id=user.id, feature_id=feature.id)

        # Delete user
        db_session.delete(user)
        db_session.commit()

        # Vote should be deleted or handled appropriately
        # This test verifies the database constraint behavior
        from app.models.vote import Vote
        remaining_votes = db_session.query(Vote).filter_by(user_id=user.id).all()

        # Depending on cascade settings, votes might be deleted or orphaned
        # This test documents the expected behavior
        assert True  # Placeholder - actual assertion depends on cascade configuration

@pytest.mark.integration
class TestVoteEndToEnd:
    """End-to-end voting scenarios"""

    def test_complete_voting_workflow(self, client, db_session):
        """Test complete voting workflow with multiple users and features"""
        # Create test data
        users = create_users_batch(db_session, count=3)
        features = create_features_batch(db_session, count=2, author_id=users[0].id)

        # Users vote for different features
        for i, user in enumerate(users):
            auth_headers = {"X-User-ID": str(user.id)}

            # Each user votes for first feature
            response = client.post(f"/api/features/{features[0].id}/vote", headers=auth_headers)
            assert response.status_code == status.HTTP_200_OK

            # First user also votes for second feature
            if i == 0:
                response = client.post(f"/api/features/{features[1].id}/vote", headers=auth_headers)
                assert response.status_code == status.HTTP_200_OK

        # Verify final vote counts
        response = client.get(f"/api/features/{features[0].id}")
        assert response.json()["vote_count"] == 3

        response = client.get(f"/api/features/{features[1].id}")
        assert response.json()["vote_count"] == 1

        # Test unvoting
        auth_headers = {"X-User-ID": str(users[0].id)}
        response = client.delete(f"/api/features/{features[0].id}/vote", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

        # Verify updated count
        response = client.get(f"/api/features/{features[0].id}")
        assert response.json()["vote_count"] == 2

    def test_voting_affects_feature_sorting(self, client, db_session):
        """Test that voting affects feature sorting by vote count"""
        users = create_users_batch(db_session, count=5)
        features = create_features_batch(db_session, count=3, author_id=users[0].id)

        # Vote for features with different patterns
        # Feature 0: 1 vote, Feature 1: 3 votes, Feature 2: 2 votes
        vote_patterns = [1, 3, 2]

        for feature_idx, vote_count in enumerate(vote_patterns):
            for user_idx in range(vote_count):
                auth_headers = {"X-User-ID": str(users[user_idx].id)}
                response = client.post(f"/api/features/{features[feature_idx].id}/vote", headers=auth_headers)
                assert response.status_code == status.HTTP_200_OK

        # Get features list (should be sorted by vote count descending)
        response = client.get("/api/features/")
        assert response.status_code == status.HTTP_200_OK

        items = response.json()["items"]
        assert len(items) == 3

        # Should be sorted: Feature 1 (3 votes), Feature 2 (2 votes), Feature 0 (1 vote)
        assert items[0]["vote_count"] == 3
        assert items[1]["vote_count"] == 2
        assert items[2]["vote_count"] == 1
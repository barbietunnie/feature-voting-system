import pytest
from fastapi import status
from tests.factories import create_users_batch, create_features_batch

@pytest.mark.integration
class TestFullUserWorkflow:
    """Test complete user workflows from creation to voting"""

    def test_complete_user_journey(self, client, db_session):
        """Test complete user journey: register, create feature, vote"""
        # 1. Create user
        user_data = {"username": "journey_user", "email": "journey@example.com"}
        response = client.post("/api/users/", json=user_data)
        assert response.status_code == status.HTTP_201_CREATED
        user = response.json()
        auth_headers = {"X-User-ID": str(user["id"])}

        # 2. Create feature
        feature_data = {
            "title": "User Journey Feature",
            "description": "A feature created during user journey test"
        }
        response = client.post("/api/features/", json=feature_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        feature = response.json()
        assert feature["author_id"] == user["id"]
        assert feature["vote_count"] == 0

        # 3. Vote for own feature (if allowed) or another user's feature
        # Create another user and feature for voting
        other_user_data = {"username": "other_user", "email": "other@example.com"}
        response = client.post("/api/users/", json=other_user_data)
        other_user = response.json()

        other_feature_data = {
            "title": "Other User Feature",
            "description": "Feature by another user for voting test"
        }
        other_auth_headers = {"X-User-ID": str(other_user["id"])}
        response = client.post("/api/features/", json=other_feature_data, headers=other_auth_headers)
        other_feature = response.json()

        # First user votes for other user's feature
        response = client.post(f"/api/features/{other_feature['id']}/vote", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["vote_count"] == 1

        # 4. Verify feature list shows updated vote count
        response = client.get("/api/features/")
        assert response.status_code == status.HTTP_200_OK
        features = response.json()["items"]

        voted_feature = next(f for f in features if f["id"] == other_feature["id"])
        assert voted_feature["vote_count"] == 1

        # 5. Unvote
        response = client.delete(f"/api/features/{other_feature['id']}/vote", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["vote_count"] == 0

    def test_multiple_users_collaborative_workflow(self, client, db_session):
        """Test multiple users working together"""
        # Create multiple users
        users = []
        for i in range(3):
            user_data = {"username": f"collab_user_{i}", "email": f"collab{i}@example.com"}
            response = client.post("/api/users/", json=user_data)
            users.append(response.json())

        # Each user creates a feature
        features = []
        for i, user in enumerate(users):
            feature_data = {
                "title": f"Collaborative Feature {i}",
                "description": f"Feature {i} created for collaboration test"
            }
            auth_headers = {"X-User-ID": str(user["id"])}
            response = client.post("/api/features/", json=feature_data, headers=auth_headers)
            features.append(response.json())

        # Users vote for each other's features
        for user_idx, user in enumerate(users):
            auth_headers = {"X-User-ID": str(user["id"])}
            for feature_idx, feature in enumerate(features):
                # Users don't vote for their own features (if that's a business rule)
                if user_idx != feature_idx:
                    response = client.post(f"/api/features/{feature['id']}/vote", headers=auth_headers)
                    assert response.status_code == status.HTTP_200_OK

        # Verify vote counts
        response = client.get("/api/features/")
        features_list = response.json()["items"]

        for feature in features_list:
            # Each feature should have 2 votes (from the other 2 users)
            assert feature["vote_count"] == 2

@pytest.mark.integration
class TestFeatureManagementWorkflow:
    """Test feature management workflows"""

    def test_feature_lifecycle_management(self, client, db_session, create_test_user):
        """Test complete feature lifecycle"""
        user = create_test_user()
        auth_headers = {"X-User-ID": str(user.id)}

        # 1. Create feature
        feature_data = {
            "title": "Lifecycle Feature",
            "description": "Testing feature lifecycle management"
        }
        response = client.post("/api/features/", json=feature_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        feature = response.json()

        # 2. Read feature
        response = client.get(f"/api/features/{feature['id']}")
        assert response.status_code == status.HTTP_200_OK
        retrieved_feature = response.json()
        assert retrieved_feature["title"] == feature_data["title"]

        # 3. Update feature
        update_data = {
            "title": "Updated Lifecycle Feature",
            "description": "Updated description for lifecycle test"
        }
        response = client.put(f"/api/features/{feature['id']}", json=update_data, headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        updated_feature = response.json()
        assert updated_feature["title"] == update_data["title"]

        # 4. Verify update in list
        response = client.get("/api/features/")
        features_list = response.json()["items"]
        found_feature = next(f for f in features_list if f["id"] == feature["id"])
        assert found_feature["title"] == update_data["title"]

    def test_voting_with_feature_updates(self, client, db_session):
        """Test voting behavior when features are updated"""
        # Create users and feature
        users = create_users_batch(db_session, count=2)
        feature_user = users[0]
        voter_user = users[1]

        # Create feature
        feature_data = {
            "title": "Votable Feature",
            "description": "Feature that will receive votes and updates"
        }
        feature_auth = {"X-User-ID": str(feature_user.id)}
        response = client.post("/api/features/", json=feature_data, headers=feature_auth)
        feature = response.json()

        # Vote for feature
        voter_auth = {"X-User-ID": str(voter_user.id)}
        response = client.post(f"/api/features/{feature['id']}/vote", headers=voter_auth)
        assert response.status_code == status.HTTP_200_OK

        # Update feature
        update_data = {"title": "Updated Votable Feature"}
        response = client.put(f"/api/features/{feature['id']}", json=update_data, headers=feature_auth)
        assert response.status_code == status.HTTP_200_OK

        # Verify vote count is preserved
        response = client.get(f"/api/features/{feature['id']}")
        updated_feature = response.json()
        assert updated_feature["vote_count"] == 1
        assert updated_feature["title"] == update_data["title"]

@pytest.mark.integration
class TestVotingSystemIntegration:
    """Test voting system integration across components"""

    def test_vote_count_consistency_across_endpoints(self, client, db_session):
        """Test vote count consistency across different API endpoints"""
        # Create test data
        users = create_users_batch(db_session, count=3)
        features = create_features_batch(db_session, count=2, author_id=users[0].id)

        # Multiple users vote
        for user in users[1:]:  # Skip feature author
            for feature in features:
                auth_headers = {"X-User-ID": str(user.id)}
                response = client.post(f"/api/features/{feature.id}/vote", headers=auth_headers)
                assert response.status_code == status.HTTP_200_OK

        # Check vote counts via different endpoints
        for feature in features:
            # 1. Via individual feature endpoint
            response = client.get(f"/api/features/{feature.id}")
            individual_count = response.json()["vote_count"]

            # 2. Via features list endpoint
            response = client.get("/api/features/")
            features_list = response.json()["items"]
            list_feature = next(f for f in features_list if f["id"] == feature.id)
            list_count = list_feature["vote_count"]

            # 3. Via vote endpoint response
            auth_headers = {"X-User-ID": str(users[0].id)}
            response = client.post(f"/api/features/{feature.id}/vote", headers=auth_headers)
            if response.status_code == status.HTTP_200_OK:
                vote_endpoint_count = response.json()["vote_count"]
                assert vote_endpoint_count == individual_count + 1

            # Verify consistency
            assert individual_count == list_count == 2  # 2 users voted

    def test_concurrent_operations_integration(self, client, db_session):
        """Test concurrent operations across different endpoints"""
        import threading
        import time

        # Create test data
        user = create_users_batch(db_session, count=1)[0]
        feature = create_features_batch(db_session, count=1, author_id=user.id)[0]

        # Create additional voters
        voters = create_users_batch(db_session, count=5)

        results = []

        def concurrent_operations(voter_user, operation_type):
            auth_headers = {"X-User-ID": str(voter_user.id)}

            if operation_type == "vote":
                response = client.post(f"/api/features/{feature.id}/vote", headers=auth_headers)
            elif operation_type == "get_feature":
                response = client.get(f"/api/features/{feature.id}")
            elif operation_type == "list_features":
                response = client.get("/api/features/")

            results.append({
                "operation": operation_type,
                "status": response.status_code,
                "user_id": voter_user.id
            })

        # Run concurrent operations
        threads = []

        # Voting threads
        for voter in voters:
            thread = threading.Thread(target=concurrent_operations, args=(voter, "vote"))
            threads.append(thread)

        # Reading threads
        for _ in range(3):
            thread = threading.Thread(target=concurrent_operations, args=(voters[0], "get_feature"))
            threads.append(thread)
            thread = threading.Thread(target=concurrent_operations, args=(voters[0], "list_features"))
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Verify results
        vote_results = [r for r in results if r["operation"] == "vote"]
        read_results = [r for r in results if r["operation"] in ["get_feature", "list_features"]]

        # All votes should succeed
        successful_votes = [r for r in vote_results if r["status"] == status.HTTP_200_OK]
        assert len(successful_votes) == 5

        # All reads should succeed
        successful_reads = [r for r in read_results if r["status"] == status.HTTP_200_OK]
        assert len(successful_reads) == 6

@pytest.mark.integration
class TestPaginationIntegration:
    """Test pagination across different scenarios"""

    def test_pagination_with_voting_and_sorting(self, client, db_session):
        """Test pagination with voting affecting sort order"""
        # Create many features with different vote patterns
        users = create_users_batch(db_session, count=10)
        features = create_features_batch(db_session, count=25, author_id=users[0].id)

        # Create varied voting patterns
        vote_patterns = [5, 10, 1, 15, 3, 8, 2, 12, 7, 4] * 3  # Repeat for 25+ features

        for i, feature in enumerate(features[:10]):  # Vote on first 10 features
            vote_count = vote_patterns[i]
            for j in range(min(vote_count, len(users)-1)):  # Don't exceed available voters
                voter = users[j+1]  # Skip feature author
                auth_headers = {"X-User-ID": str(voter.id)}
                response = client.post(f"/api/features/{feature.id}/vote", headers=auth_headers)
                if response.status_code != status.HTTP_200_OK:
                    break  # Stop if we run out of unique voters

        # Test pagination with sorting
        response = client.get("/api/features/?page=1&page_size=5")
        assert response.status_code == status.HTTP_200_OK

        page1_data = response.json()
        assert page1_data["page"] == 1
        assert page1_data["page_size"] == 5
        assert len(page1_data["items"]) == 5

        # Verify sorting (highest votes first)
        page1_items = page1_data["items"]
        for i in range(len(page1_items) - 1):
            assert page1_items[i]["vote_count"] >= page1_items[i+1]["vote_count"]

        # Test second page
        response = client.get("/api/features/?page=2&page_size=5")
        page2_data = response.json()
        assert page2_data["page"] == 2
        assert len(page2_data["items"]) == 5

        # Verify no overlap between pages
        page1_ids = {item["id"] for item in page1_items}
        page2_ids = {item["id"] for item in page2_data["items"]}
        assert page1_ids.isdisjoint(page2_ids)

@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Test error handling across integrated workflows"""

    def test_cascade_error_handling(self, client, db_session, create_test_user):
        """Test error handling when operations depend on each other"""
        user = create_test_user()
        auth_headers = {"X-User-ID": str(user.id)}

        # Try to vote for non-existent feature
        response = client.post("/api/features/999/vote", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Try to update non-existent feature
        update_data = {"title": "Updated Title"}
        response = client.put("/api/features/999", json=update_data, headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Try to vote with invalid authentication
        response = client.post("/api/features/1/vote", headers={"X-User-ID": "invalid"})
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED]

    def test_data_consistency_on_errors(self, client, db_session):
        """Test that data remains consistent when operations fail"""
        # Create initial state
        users = create_users_batch(db_session, count=2)
        feature = create_features_batch(db_session, count=1, author_id=users[0].id)[0]

        auth_headers = {"X-User-ID": str(users[1].id)}

        # Successful vote
        response = client.post(f"/api/features/{feature.id}/vote", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        initial_count = response.json()["vote_count"]

        # Failed operations should not affect vote count
        # Try duplicate vote
        response = client.post(f"/api/features/{feature.id}/vote", headers=auth_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Try invalid update
        invalid_auth = {"X-User-ID": "999"}
        response = client.put(f"/api/features/{feature.id}",
                            json={"title": "Unauthorized Update"},
                            headers=invalid_auth)
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND]

        # Verify vote count unchanged
        response = client.get(f"/api/features/{feature.id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["vote_count"] == initial_count

@pytest.mark.integration
class TestPerformanceIntegration:
    """Test system performance under load"""

    def test_bulk_operations_performance(self, client, db_session):
        """Test performance with bulk operations"""
        import time

        # Create many users
        start_time = time.time()
        users = create_users_batch(db_session, count=20)
        user_creation_time = time.time() - start_time

        # Create many features
        start_time = time.time()
        features = create_features_batch(db_session, count=50, author_id=users[0].id)
        feature_creation_time = time.time() - start_time

        # Bulk voting
        start_time = time.time()
        vote_count = 0
        for user in users[1:10]:  # 9 users vote for first 10 features
            auth_headers = {"X-User-ID": str(user.id)}
            for feature in features[:10]:
                response = client.post(f"/api/features/{feature.id}/vote", headers=auth_headers)
                if response.status_code == status.HTTP_200_OK:
                    vote_count += 1

        voting_time = time.time() - start_time

        # Test list performance with many items
        start_time = time.time()
        response = client.get("/api/features/?page_size=50")
        assert response.status_code == status.HTTP_200_OK
        list_time = time.time() - start_time

        # Performance assertions (adjust thresholds as needed)
        assert user_creation_time < 5.0  # Should create 20 users in < 5 seconds
        assert feature_creation_time < 5.0  # Should create 50 features in < 5 seconds
        assert voting_time < 10.0  # Should handle bulk voting in < 10 seconds
        assert list_time < 2.0  # Should list features in < 2 seconds
        assert vote_count > 0  # At least some votes should succeed

    def test_concurrent_user_simulation(self, client, db_session):
        """Simulate multiple users using the system concurrently"""
        import threading
        import random

        # Create base data
        users = create_users_batch(db_session, count=10)
        features = create_features_batch(db_session, count=5, author_id=users[0].id)

        results = {"votes": 0, "reads": 0, "errors": 0}
        results_lock = threading.Lock()

        def simulate_user_activity(user):
            """Simulate random user activity"""
            auth_headers = {"X-User-ID": str(user.id)}

            for _ in range(5):  # Each user performs 5 random actions
                action = random.choice(["vote", "read_list", "read_feature"])

                try:
                    if action == "vote":
                        feature = random.choice(features)
                        response = client.post(f"/api/features/{feature.id}/vote", headers=auth_headers)
                        if response.status_code == status.HTTP_200_OK:
                            with results_lock:
                                results["votes"] += 1
                        elif response.status_code == status.HTTP_400_BAD_REQUEST:
                            pass  # Expected for duplicate votes
                        else:
                            with results_lock:
                                results["errors"] += 1

                    elif action == "read_list":
                        response = client.get("/api/features/")
                        if response.status_code == status.HTTP_200_OK:
                            with results_lock:
                                results["reads"] += 1
                        else:
                            with results_lock:
                                results["errors"] += 1

                    elif action == "read_feature":
                        feature = random.choice(features)
                        response = client.get(f"/api/features/{feature.id}")
                        if response.status_code == status.HTTP_200_OK:
                            with results_lock:
                                results["reads"] += 1
                        else:
                            with results_lock:
                                results["errors"] += 1

                except Exception:
                    with results_lock:
                        results["errors"] += 1

        # Run concurrent user simulations
        threads = []
        for user in users:
            thread = threading.Thread(target=simulate_user_activity, args=(user,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Verify system handled concurrent load
        assert results["votes"] > 0
        assert results["reads"] > 0
        assert results["errors"] < results["votes"] + results["reads"]  # Error rate should be low
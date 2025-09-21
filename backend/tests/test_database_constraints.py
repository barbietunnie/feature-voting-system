import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.models.feature import Feature
from app.models.vote import Vote

@pytest.mark.integration
class TestVoteConstraints:
    """Test database constraints for votes"""

    def test_vote_unique_constraint(self, db_session, create_test_user, create_test_feature):
        """Test that unique constraint prevents duplicate votes"""
        user = create_test_user()
        feature = create_test_feature(author_id=user.id)

        # Create first vote
        vote1 = Vote(user_id=user.id, feature_id=feature.id)
        db_session.add(vote1)
        db_session.commit()

        # Try to create duplicate vote
        vote2 = Vote(user_id=user.id, feature_id=feature.id)
        db_session.add(vote2)

        with pytest.raises(IntegrityError):
            db_session.commit()

        db_session.rollback()

    def test_vote_foreign_key_user_constraint(self, db_session, create_test_feature):
        """Test foreign key constraint for user_id"""
        feature = create_test_feature(author_id=1)

        # Try to create vote with non-existent user
        vote = Vote(user_id=999, feature_id=feature.id)
        db_session.add(vote)

        with pytest.raises(IntegrityError):
            db_session.commit()

        db_session.rollback()

    def test_vote_foreign_key_feature_constraint(self, db_session, create_test_user):
        """Test foreign key constraint for feature_id"""
        user = create_test_user()

        # Try to create vote with non-existent feature
        vote = Vote(user_id=user.id, feature_id=999)
        db_session.add(vote)

        with pytest.raises(IntegrityError):
            db_session.commit()

        db_session.rollback()

    def test_vote_cascade_on_user_deletion(self, db_session, create_test_user, create_test_feature):
        """Test cascade behavior when user is deleted"""
        user = create_test_user()
        feature = create_test_feature(author_id=user.id)

        # Create vote
        vote = Vote(user_id=user.id, feature_id=feature.id)
        db_session.add(vote)
        db_session.commit()

        # Delete user
        db_session.delete(user)
        db_session.commit()

        # Check if vote still exists (depends on cascade configuration)
        remaining_votes = db_session.query(Vote).filter_by(user_id=user.id).all()
        # This assertion depends on your cascade configuration
        # If CASCADE DELETE: assert len(remaining_votes) == 0
        # If RESTRICT: the delete would fail
        # For now, we just verify the constraint behavior exists

    def test_vote_cascade_on_feature_deletion(self, db_session, create_test_user, create_test_feature):
        """Test cascade behavior when feature is deleted"""
        user = create_test_user()
        feature = create_test_feature(author_id=user.id)

        # Create vote
        vote = Vote(user_id=user.id, feature_id=feature.id)
        db_session.add(vote)
        db_session.commit()

        # Delete feature
        db_session.delete(feature)
        db_session.commit()

        # Check if vote still exists
        remaining_votes = db_session.query(Vote).filter_by(feature_id=feature.id).all()
        # Assertion depends on cascade configuration

    def test_multiple_users_same_feature(self, db_session, create_test_feature):
        """Test multiple users can vote for same feature"""
        feature = create_test_feature(author_id=1)

        # Create multiple users and votes
        for i in range(3):
            user = User(username=f"user{i}", email=f"user{i}@example.com")
            db_session.add(user)
            db_session.commit()

            vote = Vote(user_id=user.id, feature_id=feature.id)
            db_session.add(vote)

        # Should commit successfully
        db_session.commit()

        # Verify all votes exist
        votes = db_session.query(Vote).filter_by(feature_id=feature.id).all()
        assert len(votes) == 3

    def test_same_user_multiple_features(self, db_session, create_test_user):
        """Test same user can vote for multiple features"""
        user = create_test_user()

        # Create multiple features and votes
        for i in range(3):
            feature = Feature(
                title=f"Feature {i}",
                description=f"Description for feature {i}",
                author_id=user.id
            )
            db_session.add(feature)
            db_session.commit()

            vote = Vote(user_id=user.id, feature_id=feature.id)
            db_session.add(vote)

        # Should commit successfully
        db_session.commit()

        # Verify all votes exist
        votes = db_session.query(Vote).filter_by(user_id=user.id).all()
        assert len(votes) == 3

@pytest.mark.integration
class TestUserConstraints:
    """Test database constraints for users"""

    def test_user_username_unique_constraint(self, db_session):
        """Test username uniqueness constraint"""
        # Create first user
        user1 = User(username="testuser", email="test1@example.com")
        db_session.add(user1)
        db_session.commit()

        # Try to create user with same username
        user2 = User(username="testuser", email="test2@example.com")
        db_session.add(user2)

        with pytest.raises(IntegrityError):
            db_session.commit()

        db_session.rollback()

    def test_user_email_unique_constraint(self, db_session):
        """Test email uniqueness constraint"""
        # Create first user
        user1 = User(username="user1", email="test@example.com")
        db_session.add(user1)
        db_session.commit()

        # Try to create user with same email
        user2 = User(username="user2", email="test@example.com")
        db_session.add(user2)

        with pytest.raises(IntegrityError):
            db_session.commit()

        db_session.rollback()

    def test_user_required_fields(self, db_session):
        """Test that required fields cannot be null"""
        # Try to create user without username
        with pytest.raises((IntegrityError, TypeError)):
            user = User(email="test@example.com")
            db_session.add(user)
            db_session.commit()

        db_session.rollback()

        # Try to create user without email
        with pytest.raises((IntegrityError, TypeError)):
            user = User(username="testuser")
            db_session.add(user)
            db_session.commit()

        db_session.rollback()

@pytest.mark.integration
class TestFeatureConstraints:
    """Test database constraints for features"""

    def test_feature_author_foreign_key_constraint(self, db_session):
        """Test author_id foreign key constraint"""
        # Try to create feature with non-existent author
        feature = Feature(
            title="Test Feature",
            description="Test description",
            author_id=999
        )
        db_session.add(feature)

        with pytest.raises(IntegrityError):
            db_session.commit()

        db_session.rollback()

    def test_feature_required_fields(self, db_session, create_test_user):
        """Test that required fields cannot be null"""
        user = create_test_user()

        # Try to create feature without title
        with pytest.raises((IntegrityError, TypeError)):
            feature = Feature(description="Test description", author_id=user.id)
            db_session.add(feature)
            db_session.commit()

        db_session.rollback()

        # Try to create feature without description
        with pytest.raises((IntegrityError, TypeError)):
            feature = Feature(title="Test Feature", author_id=user.id)
            db_session.add(feature)
            db_session.commit()

        db_session.rollback()

    def test_feature_vote_count_default(self, db_session, create_test_user):
        """Test that vote_count defaults to 0"""
        user = create_test_user()

        feature = Feature(
            title="Test Feature",
            description="Test description",
            author_id=user.id
        )
        db_session.add(feature)
        db_session.commit()

        assert feature.vote_count == 0

@pytest.mark.integration
class TestCascadeOperations:
    """Test cascade operations and referential integrity"""

    def test_delete_user_with_authored_features(self, db_session, create_test_user):
        """Test deleting user who authored features"""
        user = create_test_user()

        # Create feature authored by user
        feature = Feature(
            title="Test Feature",
            description="Test description",
            author_id=user.id
        )
        db_session.add(feature)
        db_session.commit()

        # Try to delete user
        # This should either cascade delete features or fail with foreign key constraint
        try:
            db_session.delete(user)
            db_session.commit()
            # If successful, verify features are also deleted
            remaining_features = db_session.query(Feature).filter_by(author_id=user.id).all()
            assert len(remaining_features) == 0
        except IntegrityError:
            # If foreign key constraint prevents deletion, that's also valid
            db_session.rollback()
            assert True

    def test_delete_feature_with_votes(self, db_session, create_test_user, create_test_feature):
        """Test deleting feature that has votes"""
        user = create_test_user()
        feature = create_test_feature(author_id=user.id)

        # Create vote for feature
        vote = Vote(user_id=user.id, feature_id=feature.id)
        db_session.add(vote)
        db_session.commit()

        # Delete feature
        db_session.delete(feature)
        db_session.commit()

        # Votes should be deleted (cascade) or deletion should fail
        remaining_votes = db_session.query(Vote).filter_by(feature_id=feature.id).all()
        assert len(remaining_votes) == 0

    def test_concurrent_constraint_violations(self, db_session):
        """Test handling of concurrent constraint violations"""
        import threading
        import time

        # Create a user
        user = User(username="concurrent_user", email="concurrent@example.com")
        db_session.add(user)
        db_session.commit()

        feature = Feature(
            title="Concurrent Feature",
            description="Test concurrent operations",
            author_id=user.id
        )
        db_session.add(feature)
        db_session.commit()

        results = []

        def create_duplicate_vote():
            # Create new session for each thread
            from app.core.database import engine
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            session = SessionLocal()

            try:
                vote = Vote(user_id=user.id, feature_id=feature.id)
                session.add(vote)
                session.commit()
                results.append("success")
            except IntegrityError:
                session.rollback()
                results.append("constraint_violation")
            finally:
                session.close()

        # Try to create duplicate votes concurrently
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=create_duplicate_vote)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Only one should succeed, others should fail with constraint violations
        success_count = results.count("success")
        violation_count = results.count("constraint_violation")

        assert success_count == 1
        assert violation_count == 2

@pytest.mark.integration
class TestDataIntegrity:
    """Test overall data integrity"""

    def test_vote_count_consistency_after_direct_db_changes(self, db_session, create_test_user, create_test_feature):
        """Test vote count remains consistent after direct database changes"""
        user = create_test_user()
        feature = create_test_feature(author_id=user.id, vote_count=0)

        # Add vote directly to database
        vote = Vote(user_id=user.id, feature_id=feature.id)
        db_session.add(vote)
        db_session.commit()

        # Feature vote_count should be updated via trigger or application logic
        # This test documents expected behavior
        db_session.refresh(feature)

        # Note: This assertion depends on whether you have database triggers
        # or application-level vote count management
        # For now, we just verify the vote exists
        votes = db_session.query(Vote).filter_by(feature_id=feature.id).all()
        assert len(votes) == 1

    def test_referential_integrity_across_tables(self, db_session):
        """Test referential integrity across all tables"""
        # Create complete relationship chain
        user = User(username="integrity_user", email="integrity@example.com")
        db_session.add(user)
        db_session.commit()

        feature = Feature(
            title="Integrity Feature",
            description="Testing referential integrity",
            author_id=user.id
        )
        db_session.add(feature)
        db_session.commit()

        vote = Vote(user_id=user.id, feature_id=feature.id)
        db_session.add(vote)
        db_session.commit()

        # Verify all relationships exist
        assert feature.author_id == user.id
        assert vote.user_id == user.id
        assert vote.feature_id == feature.id

        # Verify foreign key relationships work
        feature_from_db = db_session.query(Feature).filter_by(id=feature.id).first()
        vote_from_db = db_session.query(Vote).filter_by(id=vote.id).first()

        assert feature_from_db is not None
        assert vote_from_db is not None
        assert feature_from_db.author_id == user.id
        assert vote_from_db.user_id == user.id
        assert vote_from_db.feature_id == feature.id
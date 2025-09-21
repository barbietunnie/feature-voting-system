import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def test_db():
    """Create a fresh database for each test function"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(test_db):
    """Create a database session for a test"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database session override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

@pytest.fixture
def authenticated_client(client):
    """Create a test client with authentication header"""
    client.headers.update({"X-User-ID": "1"})
    return client

@pytest.fixture
def auth_headers():
    """Return authentication headers for manual requests"""
    return {"X-User-ID": "1"}

@pytest.fixture
def multi_user_auth_headers():
    """Return authentication headers for multiple users"""
    return [
        {"X-User-ID": "1"},
        {"X-User-ID": "2"},
        {"X-User-ID": "3"},
    ]

@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "username": "testuser",
        "email": "test@example.com"
    }

@pytest.fixture
def sample_feature_data():
    """Sample feature data for testing"""
    return {
        "title": "Test Feature",
        "description": "This is a test feature description that is long enough"
    }

@pytest.fixture
def invalid_feature_data():
    """Invalid feature data for validation testing"""
    return [
        {"title": "ab", "description": "This is a test feature description"},  # Title too short
        {"title": "Valid Title", "description": "short"},  # Description too short
        {"title": "", "description": "This is a test feature description"},  # Empty title
        {"title": "Valid Title", "description": ""},  # Empty description
        {"title": "a" * 101, "description": "This is a test feature description"},  # Title too long
        {"title": "Valid Title", "description": "a" * 1001},  # Description too long
    ]

@pytest.fixture
def create_test_user(db_session):
    """Factory to create test users"""
    def _create_user(username="testuser", email="test@example.com", user_id=None):
        from app.models.user import User
        user = User(username=username, email=email)
        if user_id:
            user.id = user_id
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
    return _create_user

@pytest.fixture
def create_test_feature(db_session):
    """Factory to create test features"""
    def _create_feature(title="Test Feature", description="Test description", author_id=1, vote_count=0):
        from app.models.feature import Feature
        feature = Feature(
            title=title,
            description=description,
            author_id=author_id,
            vote_count=vote_count
        )
        db_session.add(feature)
        db_session.commit()
        db_session.refresh(feature)
        return feature
    return _create_feature

@pytest.fixture
def create_test_vote(db_session):
    """Factory to create test votes"""
    def _create_vote(user_id, feature_id):
        from app.models.vote import Vote
        vote = Vote(user_id=user_id, feature_id=feature_id)
        db_session.add(vote)
        db_session.commit()
        db_session.refresh(vote)
        return vote
    return _create_vote
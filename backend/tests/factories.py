import factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from app.models.user import User
from app.models.feature import Feature
from app.models.vote import Vote

fake = Faker()

class UserFactory(SQLAlchemyModelFactory):
    """Factory for creating User instances"""

    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")

    @classmethod
    def create_batch_with_session(cls, size, session, **kwargs):
        """Create multiple users with specific session"""
        users = []
        for i in range(size):
            user = cls.build(**kwargs)
            session.add(user)
            users.append(user)
        session.commit()
        return users

class FeatureFactory(SQLAlchemyModelFactory):
    """Factory for creating Feature instances"""

    class Meta:
        model = Feature
        sqlalchemy_session_persistence = "commit"

    title = factory.Faker('sentence', nb_words=3)
    description = factory.Faker('text', max_nb_chars=200)
    author_id = 1
    vote_count = 0

    @factory.lazy_attribute
    def title(self):
        # Ensure title is between 3-100 characters
        title = fake.sentence(nb_words=3).rstrip('.')
        return title[:100] if len(title) > 100 else title

    @factory.lazy_attribute
    def description(self):
        # Ensure description is between 10-1000 characters
        desc = fake.text(max_nb_chars=200)
        if len(desc) < 10:
            desc = fake.text(max_nb_chars=500)
        return desc[:1000] if len(desc) > 1000 else desc

class VoteFactory(SQLAlchemyModelFactory):
    """Factory for creating Vote instances"""

    class Meta:
        model = Vote
        sqlalchemy_session_persistence = "commit"

    user_id = 1
    feature_id = 1

# Data generators for testing edge cases
class TestDataGenerator:
    """Generate test data for various scenarios"""

    @staticmethod
    def valid_user_data():
        """Generate valid user data"""
        return {
            "username": fake.user_name(),
            "email": fake.email()
        }

    @staticmethod
    def invalid_user_data():
        """Generate various invalid user data scenarios"""
        return [
            {"username": "", "email": "valid@example.com"},  # Empty username
            {"username": "valid", "email": ""},  # Empty email
            {"username": "valid", "email": "invalid-email"},  # Invalid email format
            {"username": "a" * 51, "email": "valid@example.com"},  # Username too long (if there's a limit)
            {"username": "valid", "email": "a" * 100 + "@example.com"},  # Email too long
        ]

    @staticmethod
    def valid_feature_data():
        """Generate valid feature data"""
        return {
            "title": fake.sentence(nb_words=3).rstrip('.'),
            "description": fake.text(max_nb_chars=200)
        }

    @staticmethod
    def invalid_feature_data():
        """Generate various invalid feature data scenarios"""
        return [
            {"title": "ab", "description": "Valid description that is long enough"},  # Title too short
            {"title": "Valid Title", "description": "short"},  # Description too short
            {"title": "", "description": "Valid description that is long enough"},  # Empty title
            {"title": "Valid Title", "description": ""},  # Empty description
            {"title": "   ", "description": "Valid description that is long enough"},  # Whitespace title
            {"title": "Valid Title", "description": "   "},  # Whitespace description
            {"title": "a" * 101, "description": "Valid description that is long enough"},  # Title too long
            {"title": "Valid Title", "description": "a" * 1001},  # Description too long
        ]

    @staticmethod
    def edge_case_strings():
        """Generate edge case strings for testing"""
        return [
            "",  # Empty string
            "   ",  # Whitespace only
            "a" * 1000,  # Very long string
            "Special chars: !@#$%^&*()",  # Special characters
            "Unicode: 你好世界 🌍",  # Unicode characters
            "SQL'; DROP TABLE users; --",  # SQL injection attempt
            "<script>alert('xss')</script>",  # XSS attempt
            "\n\r\t",  # Control characters
        ]

    @staticmethod
    def boundary_test_data():
        """Generate boundary value test data"""
        return {
            "title_min": "abc",  # Minimum valid title (3 chars)
            "title_max": "a" * 100,  # Maximum valid title (100 chars)
            "title_over": "a" * 101,  # Over maximum
            "title_under": "ab",  # Under minimum
            "desc_min": "a" * 10,  # Minimum valid description (10 chars)
            "desc_max": "a" * 1000,  # Maximum valid description (1000 chars)
            "desc_over": "a" * 1001,  # Over maximum
            "desc_under": "a" * 9,  # Under minimum
        }

# Utility functions for test data creation
def create_users_batch(session, count=5):
    """Create multiple test users"""
    users = []
    for i in range(count):
        user_data = TestDataGenerator.valid_user_data()
        user_data["username"] = f"testuser{i}"
        user_data["email"] = f"test{i}@example.com"

        user = User(**user_data)
        session.add(user)
        users.append(user)

    session.commit()
    return users

def create_features_batch(session, count=5, author_id=1):
    """Create multiple test features"""
    features = []
    for i in range(count):
        feature_data = TestDataGenerator.valid_feature_data()
        feature_data["title"] = f"Test Feature {i}"
        feature_data["author_id"] = author_id

        feature = Feature(**feature_data)
        session.add(feature)
        features.append(feature)

    session.commit()
    return features
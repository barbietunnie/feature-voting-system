from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
# Current: SQLite for easy development and testing
# Original: PostgreSQL - can be restored by setting DATABASE_URL environment variable
# Example: DATABASE_URL=postgresql://user:password@localhost:5432/feature_voting_db
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./feature_voting.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
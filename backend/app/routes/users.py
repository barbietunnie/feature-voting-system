from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from app.core.database import get_db
from app.core.exceptions import UserNotFoundException, InvalidInputException, DatabaseException
from app.schemas.user import User, UserCreate, UserUpdate
from app.models.user import User as UserModel

router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if not user.username or len(user.username.strip()) < 2:
        raise InvalidInputException("Username must be at least 2 characters long")

    if not user.email or "@" not in user.email:
        raise InvalidInputException("Valid email address is required")

    try:
        db_user = UserModel(
            username=user.username.strip(),
            email=user.email.strip().lower()
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        if "username" in str(e.orig).lower():
            raise InvalidInputException("Username already exists")
        elif "email" in str(e.orig).lower():
            raise InvalidInputException("Email already exists")
        else:
            raise DatabaseException("Failed to create user due to data constraint")

@router.get("/", response_model=List[User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    if skip < 0:
        raise InvalidInputException("Skip parameter must be non-negative")
    if limit <= 0 or limit > 1000:
        raise InvalidInputException("Limit must be between 1 and 1000")

    try:
        users = db.query(UserModel).offset(skip).limit(limit).all()
        return users
    except Exception as e:
        raise DatabaseException("Failed to retrieve users")

@router.get("/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    if user_id <= 0:
        raise InvalidInputException("User ID must be positive")

    try:
        db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user is None:
            raise UserNotFoundException()
        return db_user
    except UserNotFoundException:
        raise
    except Exception as e:
        raise DatabaseException("Failed to retrieve user")
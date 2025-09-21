from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FeatureVotingException(Exception):
    """Base exception for Feature Voting System"""
    def __init__(self, message: str = None, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

class DuplicateVoteException(FeatureVotingException):
    """Raised when user tries to vote twice for the same feature"""
    def __init__(self, message: str = "User has already voted for this feature"):
        super().__init__(message, "DUPLICATE_VOTE")

class FeatureNotFoundException(FeatureVotingException):
    """Raised when feature is not found"""
    def __init__(self, message: str = "Feature not found"):
        super().__init__(message, "FEATURE_NOT_FOUND")

class VoteNotFoundException(FeatureVotingException):
    """Raised when vote is not found"""
    def __init__(self, message: str = "Vote not found"):
        super().__init__(message, "VOTE_NOT_FOUND")

class UserNotFoundException(FeatureVotingException):
    """Raised when user is not found"""
    def __init__(self, message: str = "User not found"):
        super().__init__(message, "USER_NOT_FOUND")

class InvalidInputException(FeatureVotingException):
    """Raised when input validation fails"""
    def __init__(self, message: str = "Invalid input provided"):
        super().__init__(message, "INVALID_INPUT")

class DatabaseException(FeatureVotingException):
    """Raised when database operations fail"""
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, "DATABASE_ERROR")

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    logger.error(f"Validation error for {request.url}: {exc}")

    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation failed",
            "errors": errors,
            "type": "validation_error"
        }
    )

async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Handle database integrity constraint violations"""
    logger.error(f"Database integrity error for {request.url}: {exc}")

    error_msg = str(exc.orig)

    if "_user_feature_vote" in error_msg:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": "User has already voted for this feature",
                "type": "duplicate_vote_error"
            }
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Database constraint violation",
            "type": "integrity_error"
        }
    )

async def feature_voting_exception_handler(request: Request, exc: FeatureVotingException):
    """Handle custom Feature Voting exceptions"""
    logger.error(f"Feature voting error for {request.url}: {exc}")

    error_response = {
        "detail": exc.message or str(exc),
        "error_code": exc.error_code,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "path": str(request.url)
    }

    if isinstance(exc, DuplicateVoteException):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=error_response
        )
    elif isinstance(exc, (FeatureNotFoundException, VoteNotFoundException, UserNotFoundException)):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response
        )
    elif isinstance(exc, InvalidInputException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response
        )
    elif isinstance(exc, DatabaseException):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "error_code": "DATABASE_ERROR",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "path": str(request.url)
            }
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "path": str(request.url)
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle FastAPI HTTP exceptions with consistent format"""
    logger.warning(f"HTTP exception for {request.url}: {exc.status_code} - {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": f"HTTP_{exc.status_code}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "path": str(request.url)
        }
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error for {request.url}: {type(exc).__name__}: {exc}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred",
            "error_code": "UNEXPECTED_ERROR",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "path": str(request.url)
        }
    )
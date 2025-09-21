from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

class FeatureVotingException(Exception):
    """Base exception for Feature Voting System"""
    pass

class DuplicateVoteException(FeatureVotingException):
    """Raised when user tries to vote twice for the same feature"""
    pass

class FeatureNotFoundException(FeatureVotingException):
    """Raised when feature is not found"""
    pass

class VoteNotFoundException(FeatureVotingException):
    """Raised when vote is not found"""
    pass

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

    if isinstance(exc, DuplicateVoteException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": "User has already voted for this feature",
                "type": "duplicate_vote_error"
            }
        )
    elif isinstance(exc, FeatureNotFoundException):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail": "Feature not found",
                "type": "feature_not_found_error"
            }
        )
    elif isinstance(exc, VoteNotFoundException):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail": "Vote not found",
                "type": "vote_not_found_error"
            }
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "type": "internal_error"
        }
    )
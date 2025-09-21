from fastapi import Header, HTTPException, status
from typing import Optional

def get_current_user(x_user_id: Optional[str] = Header(None)) -> int:
    """
    Simple user authentication using X-User-ID header.
    In production, this would be replaced with proper JWT token validation.
    """
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-User-ID header is required"
        )

    try:
        user_id = int(x_user_id)
        if user_id <= 0:
            raise ValueError("User ID must be positive")
        return user_id
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
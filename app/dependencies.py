"""
FastAPI Dependencies
Dependency injection for authentication and database sessions
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import get_db
from .security import decode_access_token
from . import db_models

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/users/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> db_models.User:
    """
    Dependency to get the current authenticated user from JWT token
    
    Args:
        token: JWT token from Authorization header
        db: Database session
        
    Returns:
        Current authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    # Get user email from token
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    # Get user from database
    user = db.query(db_models.User).filter(db_models.User.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: db_models.User = Depends(get_current_user)
) -> db_models.User:
    """
    Dependency to ensure current user is active
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Active user
        
    Raises:
        HTTPException: If user account is not active
    """
    if current_user.status != db_models.UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active"
        )
    return current_user

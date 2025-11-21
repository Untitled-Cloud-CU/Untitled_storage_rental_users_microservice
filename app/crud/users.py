"""
CRUD operations for Users
Database access layer for user operations
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import db_models, schemas
from ..security import get_password_hash, verify_password


def get_user(db: Session, user_id: int) -> Optional[db_models.User]:
    """Get a user by ID"""
    return db.query(db_models.User).filter(db_models.User.user_id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[db_models.User]:
    """Get a user by email"""
    return db.query(db_models.User).filter(db_models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[db_models.User]:
    """Get all users with pagination"""
    return db.query(db_models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate) -> db_models.User:
    """
    Create a new user with hashed password
    
    Args:
        db: Database session
        user: User creation data
        
    Returns:
        Created user object
    """
    # Hash the password
    hashed_password = get_password_hash(user.password)
    
    # Create user object
    db_user = db_models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        hashed_password=hashed_password,
        phone=user.phone,
        address=user.address,
        city=user.city,
        state=user.state,
        zip_code=user.zip_code,
        status=db_models.UserStatus.ACTIVE
    )
    
    # Add to database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


def update_user(db: Session, user_id: int, user: schemas.UserUpdate) -> Optional[db_models.User]:
    """
    Update user information
    
    Args:
        db: Database session
        user_id: ID of user to update
        user: Updated user data
        
    Returns:
        Updated user object or None if not found
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    # Update only provided fields
    update_data = user.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """
    Delete a user
    
    Args:
        db: Database session
        user_id: ID of user to delete
        
    Returns:
        True if deleted, False if not found
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    
    return True


def authenticate_user(db: Session, email: str, password: str) -> Optional[db_models.User]:
    """
    Authenticate a user with email and password
    
    Args:
        db: Database session
        email: User email
        password: Plain text password
        
    Returns:
        User object if authenticated, None otherwise
    """
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def update_user_status(db: Session, user_id: int, status: db_models.UserStatus) -> Optional[db_models.User]:
    """
    Update user account status
    
    Args:
        db: Database session
        user_id: ID of user to update
        status: New status
        
    Returns:
        Updated user object or None if not found
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    db_user.status = status
    db.commit()
    db.refresh(db_user)
    
    return db_user

"""
User endpoints
Handles all user-related API operations - SPRINT 2 IMPLEMENTATION
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta

from .. import schemas, crud
from ..database import get_db
from ..security import create_access_token, verify_password
from ..dependencies import get_current_user
from ..config import settings
import httpx

router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"]
)


@router.get("/", response_model=List[schemas.User])
def get_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Retrieve list of all users with pagination
    
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    """
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific user by ID
    
    - **user_id**: The ID of the user to retrieve
    """
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user
    
    - **user**: User information including password
    """
    # Check if user already exists
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return crud.create_user(db=db, user=user)


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int,
    user: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Update an existing user's information
    
    - **user_id**: The ID of the user to update
    - **user**: Updated user information
    
    Requires authentication. Users can only update their own information.
    """
    # Check if user is updating their own account
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    # Check if email is being updated to an existing email
    if user.email:
        existing_user = crud.get_user_by_email(db, email=user.email)
        if existing_user and existing_user.user_id != user_id:
            raise HTTPException(status_code=400, detail="Email already in use")
    
    db_user = crud.update_user(db, user_id=user_id, user=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return db_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Delete a user account
    
    - **user_id**: The ID of the user to delete
    
    Requires authentication. Users can only delete their own account.
    """
    # Check if user is deleting their own account
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user"
        )
    
    success = crud.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    return None


@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account
    
    This endpoint creates a new user with validated information
    and hashed password
    
    - **user**: User registration information
    """
    # Check if user already exists
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return crud.create_user(db=db, user=user)


@router.post("/login", response_model=schemas.LoginResponse)
def login_user(credentials: schemas.LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return access token
    
    - **credentials**: Email and password for authentication
    """
    # Authenticate user
    user = crud.authenticate_user(db, email=credentials.email, password=credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.user_id},
        expires_delta=access_token_expires
    )
    
    return {
        "user_id": user.user_id,
        "email": user.email,
        "token": access_token,
        "token_type": "bearer",
        "message": "Login successful"
    }


@router.get("/{user_id}/rentals")
async def get_user_rentals(
    user_id: int,
    active_only: bool = Query(False, description="Return only active rentals"),
    current_user = Depends(get_current_user)
):
    """
    Get all rentals for a specific user
    
    - **user_id**: The ID of the user
    - **active_only**: Filter to show only active rentals
    
    Requires authentication. Users can only view their own rentals.
    """
    # Check authorization
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user's rentals"
        )
    
    # Call orders service to get rentals
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.orders_service_url}/api/v1/rentals/user/{user_id}",
                params={"active_only": active_only}
            )
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return []
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Orders service unavailable"
                )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not connect to orders service"
        )


@router.get("/{user_id}/rentals/{rental_id}")
async def get_user_rental_details(
    user_id: int,
    rental_id: int,
    current_user = Depends(get_current_user)
):
    """
    Get detailed information about a specific rental
    
    - **user_id**: The ID of the user
    - **rental_id**: The ID of the rental
    
    Requires authentication. Users can only view their own rentals.
    """
    # Check authorization
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this rental"
        )
    
    # Call orders service to get rental details
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.orders_service_url}/api/v1/rentals/{rental_id}"
            )
            if response.status_code == 200:
                rental_data = response.json()
                # Verify the rental belongs to the user
                if rental_data.get("user_id") != user_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Not authorized to view this rental"
                    )
                return rental_data
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="Rental not found")
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Orders service unavailable"
                )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not connect to orders service"
        )

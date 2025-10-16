"""
User endpoints
Handles all user-related API operations
"""
from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from ..models import (
    User, 
    UserCreate, 
    UserUpdate, 
    LoginRequest, 
    LoginResponse, 
    UserRental
)

router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"]
)

# Mock data for demonstration
MOCK_USER = {
    "user_id": 1,
    "first_name": "John",
    "last_name": "Smith",
    "email": "john.smith@email.com",
    "phone": "555-0101",
    "address": "123 Main St",
    "city": "Seattle",
    "state": "WA",
    "zip_code": "98101",
    "status": "active",
    "created_at": "2024-01-15T10:00:00",
    "updated_at": "2024-01-15T10:00:00"
}


@router.get("/", response_model=List[User])
async def get_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return")
):
    """
    Retrieve list of all users with pagination
    
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    """
    return {
        "message": "NOT IMPLEMENTED",
        "note": "Will return paginated list of users"
    }


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int):
    """
    Retrieve a specific user by ID
    
    - **user_id**: The ID of the user to retrieve
    """
    if user_id == 1:
        return MOCK_USER
    return {
        "message": "NOT IMPLEMENTED",
        "user_id": user_id
    }


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """
    Create a new user
    
    - **user**: User information including password
    """
    return {
        "message": "NOT IMPLEMENTED",
        "note": "Will create new user",
        "email": user.email
    }


@router.put("/{user_id}", response_model=User)
async def update_user(user_id: int, user: UserUpdate):
    """
    Update an existing user's information
    
    - **user_id**: The ID of the user to update
    - **user**: Updated user information
    """
    return {
        "message": "NOT IMPLEMENTED",
        "user_id": user_id,
        "updated_fields": user.dict(exclude_unset=True)
    }


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    """
    Delete a user account
    
    - **user_id**: The ID of the user to delete
    """
    return {
        "message": "NOT IMPLEMENTED",
        "user_id": user_id
    }


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
    """
    Register a new user account
    
    This endpoint creates a new user with validated information
    and hashed password (in future implementation)
    
    - **user**: User registration information
    """
    return {
        "message": "NOT IMPLEMENTED",
        "note": "Will register new user with hashed password",
        "email": user.email
    }


@router.post("/login", response_model=LoginResponse)
async def login_user(credentials: LoginRequest):
    """
    Authenticate user and return access token
    
    - **credentials**: Email and password for authentication
    """
    return {
        "user_id": 1,
        "email": credentials.email,
        "token": "mock_jwt_token_12345",
        "message": "NOT IMPLEMENTED - Will return JWT token"
    }


@router.get("/{user_id}/rentals", response_model=List[UserRental])
async def get_user_rentals(
    user_id: int,
    active_only: bool = Query(False, description="Return only active rentals")
):
    """
    Get all rentals for a specific user
    
    - **user_id**: The ID of the user
    - **active_only**: Filter to show only active rentals
    """
    return {
        "message": "NOT IMPLEMENTED",
        "user_id": user_id,
        "active_only": active_only,
        "note": "Will return list of user's rentals"
    }


@router.get("/{user_id}/rentals/{rental_id}")
async def get_user_rental_details(user_id: int, rental_id: int):
    """
    Get detailed information about a specific rental
    
    - **user_id**: The ID of the user
    - **rental_id**: The ID of the rental
    """
    return {
        "message": "NOT IMPLEMENTED",
        "user_id": user_id,
        "rental_id": rental_id
    }

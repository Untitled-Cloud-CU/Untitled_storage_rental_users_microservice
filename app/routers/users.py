"""
User endpoints
Handles all user-related API operations
"""
from fastapi import APIRouter, HTTPException, status, Query
from ..db_models import UserDB
from typing import List, Optional
from ..models import (
    User, 
    UserCreate, 
    UserUpdate, 
    LoginRequest, 
    LoginResponse, 
    UserRental
)

from fastapi import Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..crud_users import create_user as create_user_db
from ..crud_users import get_users as get_users_db
import hashlib

import uuid
import threading
import time

from .auth import get_current_user
from ..db_models import UserDB


# In-memory job status storage
JOB_STORE = {}



def process_email_verification(job_id: str):
    """
    Simulates a long-running async job.
    """
    time.sleep(5)  # Fake 5-second operation
    JOB_STORE[job_id] = "completed"




def generate_etag(user):
    """
    Creates an ETag based on user_id + updated_at timestamp.
    """
    raw = f"{user.user_id}-{user.updated_at.isoformat()}"
    return hashlib.sha256(raw.encode()).hexdigest()
def add_hateoas(user):
    return {
        **User.model_validate(user).model_dump(),
        "_links": {
            "self": f"/api/v1/users/{user.user_id}",
            "update": f"/api/v1/users/{user.user_id}",
            "delete": f"/api/v1/users/{user.user_id}",
            "rentals": f"/api/v1/users/{user.user_id}/rentals"
        }
    }



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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


from ..crud_users import get_users as get_users_db

@router.get("/", response_model=List[User])
async def get_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state"),
    status: Optional[str] = Query(None, description="Filter by user status (active, inactive, suspended)"),
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Retrieve list of users with pagination + filtering.
    """
    users = get_users_db(
        db=db,
        skip=skip,
        limit=limit,
        city=city,
        state=state,
        status=status
    )

    # Add HATEOAS links
    response = []
    for u in users:
        user_dict = User.model_validate(u).model_dump()
        user_dict["_links"] = {
            "self": f"/api/v1/users/{u.user_id}",
            "update": f"/api/v1/users/{u.user_id}",
            "delete": f"/api/v1/users/{u.user_id}"
        }
        response.append(user_dict)

    return response



from fastapi import Request
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi import HTTPException

@router.get("/{user_id}", response_model=User)
async def get_user_by_id(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Retrieve a specific user using ETag caching.
    If client sends `If-None-Match` and ETag matches, return 304.
    """

    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden: cannot view another user")

    # Fetch from DB
    user = db.query(UserDB).filter(UserDB.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate ETag
    etag = generate_etag(user)

    # If client provided If-None-Match, compare
    client_etag = request.headers.get("if-none-match")
    if client_etag and client_etag == etag:
        # No change → return 304 Not Modified
        return JSONResponse(status_code=304, content=None)

    # Otherwise return full user object with ETag in header
    # response = JSONResponse(content=User.model_validate(user).model_dump())
    response = JSONResponse(content=add_hateoas(user))
    response.headers["ETag"] = etag
    return response


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user in the database.
    """
    new_user = create_user_db(db=db, user=user)
    # return new_user
    return add_hateoas(new_user)


from ..crud_users import update_user as update_user_db
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """
    Update a user's data.
    Supports partial updates.
    Returns updated resource with NEW ETag.
    """
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden: cannot update another user")

    # Find existing user
    existing = db.query(UserDB).filter(UserDB.user_id == user_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")

    # Optional: ETag precondition check ("If-Match")
    client_etag = request.headers.get("if-match")
    current_etag = generate_etag(existing)

    # If client uses optimistic concurrency:
    if client_etag and client_etag != current_etag:
        raise HTTPException(
            status_code=412,  # Precondition Failed
            detail="ETag does not match — resource has changed"
        )

    # Perform update
    updated_user = update_user_db(db=db, user_id=user_id, user_update=user)

    # Return UPDATED resource with NEW ETag
    new_etag = generate_etag(updated_user)
    # response = JSONResponse(content=User.model_validate(updated_user).model_dump())
    response = JSONResponse(content=add_hateoas(updated_user))

    response.headers["ETag"] = new_etag
    return response


from ..crud_users import delete_user as delete_user_db

@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """
    Delete a user.
    Returns 204 No Content.
    Supports optional ETag precondition with If-Match header.
    """
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden: cannot delete another user")

    # Check if user exists first
    db_user = db.query(UserDB).filter(UserDB.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Optional: Support optimistic concurrency
    client_etag = request.headers.get("if-match")
    current_etag = generate_etag(db_user)

    if client_etag and client_etag != current_etag:
        raise HTTPException(
            status_code=412,
            detail="ETag does not match — cannot delete. Resource changed."
        )

    # Perform deletion
    success = delete_user_db(db=db, user_id=user_id)

    if not success:
        raise HTTPException(status_code=404, detail="User not found")

    # 204 No Content → return nothing
    return Response(status_code=204)



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
    active_only: bool = Query(False, description="Return only active rentals"),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get all rentals for a specific user
    
    - **user_id**: The ID of the user
    - **active_only**: Filter to show only active rentals
    """
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden: cannot view another user's rentals")
    return {
        "message": "NOT IMPLEMENTED",
        "user_id": user_id,
        "active_only": active_only,
        "note": "Will return list of user's rentals"
    }



@router.get("/{user_id}/rentals/{rental_id}")
async def get_user_rental_details(
    user_id: int,
    rental_id: int,
    current_user: UserDB = Depends(get_current_user),  # 🔐 NEW
):
    """
    Get detailed information about a specific rental

    - **user_id**: The ID of the user
    - **rental_id**: The ID of the rental
    """
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: cannot view another user's rental"
        )

    return {
        "message": "NOT IMPLEMENTED",
        "user_id": user_id,
        "rental_id": rental_id
    }




@router.post("/verify-email", status_code=202)
async def verify_email(request: Request):
    """
    Initiates async email verification job.
    Returns 202 Accepted + job_id + polling link.
    """

    # 1. Create a job ID
    job_id = str(uuid.uuid4())

    # 2. Mark job as pending
    JOB_STORE[job_id] = "pending"

    # 3. Start background thread
    thread = threading.Thread(target=process_email_verification, args=(job_id,))
    thread.start()

    # 4. Return 202 response with job link
    return {
        "job_id": job_id,
        "status": "accepted",
        "_links": {
            "poll": f"/api/v1/jobs/{job_id}",
            "self": "/api/v1/users/verify-email"
        }
    }
@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """
    Poll the status of an async job.
    """

    status = JOB_STORE.get(job_id)

    if status is None:
        raise HTTPException(status_code=404, detail="Invalid job_id")

    return {
        "job_id": job_id,
        "status": status,
        "_links": {
            "self": f"/api/v1/jobs/{job_id}"
        }
    }


"""
User endpoints - Enhanced with eTag, HATEOAS, and 202 Async
Handles all user-related API operations
"""
from fastapi import APIRouter, HTTPException, status, Query, Response, Header, Request, BackgroundTasks
from typing import List, Optional, Dict
from datetime import datetime
import hashlib
import uuid
import time
from ..models import (
    User, 
    UserCreate, 
    UserUpdate, 
    LoginRequest, 
    LoginResponse, 
    UserRental,
    TaskStatus,
    TaskCreate
)

router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"]
)

# Mock data for demonstration (replace with database in production)
MOCK_USERS = {
    1: {
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
        "created_at": datetime(2024, 1, 15, 10, 0, 0),
        "updated_at": datetime(2024, 1, 15, 10, 0, 0)
    },
    2: {
        "user_id": 2,
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@email.com",
        "phone": "555-0102",
        "address": "456 Oak Ave",
        "city": "Portland",
        "state": "OR",
        "zip_code": "97201",
        "status": "active",
        "created_at": datetime(2024, 1, 16, 10, 0, 0),
        "updated_at": datetime(2024, 1, 16, 10, 0, 0)
    }
}

# In-memory task storage for 202 Async (use Redis in production)
task_storage: Dict[str, dict] = {}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def add_hateoas_links(user_dict: dict, request: Request) -> dict:
    """
    Add HATEOAS links to user response
    Implements: Linked data and relative paths requirement
    """
    base_url = str(request.base_url).rstrip('/')
    user_id = user_dict["user_id"]
    
    user_dict["_links"] = {
        "self": {
            "href": f"{base_url}/api/v1/users/{user_id}",
            "method": "GET"
        },
        "update": {
            "href": f"{base_url}/api/v1/users/{user_id}",
            "method": "PUT"
        },
        "delete": {
            "href": f"{base_url}/api/v1/users/{user_id}",
            "method": "DELETE"
        },
        "rentals": {
            "href": f"{base_url}/api/v1/users/{user_id}/rentals",
            "method": "GET"
        },
        "verify-email": {
            "href": f"{base_url}/api/v1/users/{user_id}/verify-email",
            "method": "POST"
        },
        "collection": {
            "href": f"{base_url}/api/v1/users",
            "method": "GET"
        }
    }
    return user_dict


def generate_etag(user_dict: dict) -> str:
    """
    Generate ETag based on user data and updated_at timestamp
    Implements: eTag processing requirement
    """
    updated_at = user_dict["updated_at"]
    if isinstance(updated_at, datetime):
        updated_at = updated_at.isoformat()
    
    etag_data = f"{user_dict['user_id']}-{updated_at}"
    etag = hashlib.md5(etag_data.encode()).hexdigest()
    return f'"{etag}"'


def send_verification_email_task(user_id: int, task_id: str):
    """
    Background task to simulate email sending
    Implements: 202 Accepted asynchronous processing
    """
    # Simulate processing time
    time.sleep(5)
    
    # Update task status
    task_storage[task_id] = {
        "task_id": task_id,
        "status": "completed",
        "user_id": user_id,
        "message": "Verification email sent successfully",
        "started_at": task_storage[task_id]["started_at"],
        "completed_at": datetime.utcnow().isoformat()
    }


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/", response_model=List[User])
async def get_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    request: Request = None
):
    """
    Retrieve list of all users with pagination and HATEOAS links
    
    Features:
    - Pagination with skip/limit query parameters
    - HATEOAS links for each user
    
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    """
    # Get paginated users
    all_users = list(MOCK_USERS.values())
    paginated_users = all_users[skip:skip + limit]
    
    # Add HATEOAS links to each user
    users_with_links = []
    for user in paginated_users:
        user_copy = user.copy()
        user_copy = add_hateoas_links(user_copy, request)
        users_with_links.append(user_copy)
    
    return users_with_links


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    request: Request,
    if_none_match: Optional[str] = Header(None)
):
    """
    Retrieve a specific user by ID with ETag support
    
    Features:
    - ETag generation and validation (304 Not Modified)
    - HATEOAS links
    - Cache-Control headers
    
    Headers:
    - If-None-Match: ETag value for conditional GET
    
    Returns:
    - 200: User data with ETag header
    - 304: Not Modified (if ETag matches)
    - 404: User not found
    """
    # Get user
    if user_id not in MOCK_USERS:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = MOCK_USERS[user_id].copy()
    
    # Generate ETag
    etag = generate_etag(user)
    
    # Check If-None-Match header (ETag validation)
    if if_none_match and if_none_match == etag:
        # Resource hasn't changed, return 304 Not Modified
        return Response(status_code=304, headers={"ETag": etag})
    
    # Add HATEOAS links
    user = add_hateoas_links(user, request)
    
    # Convert datetime objects to ISO format for JSON serialization
    user["created_at"] = user["created_at"].isoformat()
    user["updated_at"] = user["updated_at"].isoformat()
    
    # Return response with ETag and Cache-Control headers
    return Response(
        content=str(user).replace("'", '"'),  # Simple JSON conversion
        media_type="application/json",
        headers={
            "ETag": etag,
            "Cache-Control": "max-age=60"  # Cache for 60 seconds
        }
    )


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, request: Request):
    """
    Create a new user
    
    Features:
    - Returns 201 Created status code
    - HATEOAS links in response
    - Location header with new resource URL
    
    - **user**: User information including password
    """
    # Generate new user ID
    new_id = max(MOCK_USERS.keys()) + 1 if MOCK_USERS else 1
    
    # Create new user
    new_user = {
        "user_id": new_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone": user.phone,
        "address": user.address,
        "city": user.city,
        "state": user.state,
        "zip_code": user.zip_code,
        "status": "active",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    MOCK_USERS[new_id] = new_user
    
    # Add HATEOAS links
    response_user = add_hateoas_links(new_user.copy(), request)
    
    # Convert datetime to ISO format
    response_user["created_at"] = response_user["created_at"].isoformat()
    response_user["updated_at"] = response_user["updated_at"].isoformat()
    
    return response_user


@router.put("/{user_id}", response_model=User)
async def update_user(user_id: int, user: UserUpdate, request: Request):
    """
    Update an existing user's information
    
    Features:
    - HATEOAS links in response
    - Updates timestamp automatically
    
    - **user_id**: The ID of the user to update
    - **user**: Updated user information
    """
    if user_id not in MOCK_USERS:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user
    existing_user = MOCK_USERS[user_id]
    update_data = user.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        existing_user[field] = value
    
    existing_user["updated_at"] = datetime.utcnow()
    
    # Add HATEOAS links
    response_user = add_hateoas_links(existing_user.copy(), request)
    
    # Convert datetime to ISO format
    response_user["created_at"] = response_user["created_at"].isoformat()
    response_user["updated_at"] = response_user["updated_at"].isoformat()
    
    return response_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    """
    Delete a user account
    
    - **user_id**: The ID of the user to delete
    """
    if user_id not in MOCK_USERS:
        raise HTTPException(status_code=404, detail="User not found")
    
    del MOCK_USERS[user_id]
    return None


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, request: Request):
    """
    Register a new user account
    
    Features:
    - Returns 201 Created status code
    - Password validation
    - HATEOAS links in response
    
    - **user**: User registration information
    """
    return await create_user(user, request)


@router.post("/login", response_model=LoginResponse)
async def login_user(credentials: LoginRequest):
    """
    Authenticate user and return access token
    
    - **credentials**: Email and password for authentication
    """
    # Find user by email
    user = None
    for u in MOCK_USERS.values():
        if u["email"] == credentials.email:
            user = u
            break
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    return {
        "user_id": user["user_id"],
        "email": user["email"],
        "token": "mock_jwt_token_12345",  # Replace with real JWT in production
        "token_type": "bearer",
        "message": "Login successful"
    }


# ============================================================================
# 202 ACCEPTED ASYNC ENDPOINT
# ============================================================================

@router.post("/{user_id}/verify-email", status_code=status.HTTP_202_ACCEPTED)
async def verify_email_async(
    user_id: int,
    background_tasks: BackgroundTasks,
    request: Request
):
    """
    Initiate async email verification - returns 202 Accepted immediately
    
    Features:
    - Returns 202 Accepted status code
    - Asynchronous processing with background tasks
    - Polling endpoint for status updates
    - HATEOAS links for status polling
    
    Client should poll GET /api/v1/users/tasks/{task_id} to check status
    
    - **user_id**: The ID of the user to verify
    
    Returns:
    - 202: Accepted, task created
    - 404: User not found
    """
    # Check if user exists
    if user_id not in MOCK_USERS:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create task
    task_id = str(uuid.uuid4())
    base_url = str(request.base_url).rstrip('/')
    status_url = f"{base_url}/api/v1/users/tasks/{task_id}"
    
    task_storage[task_id] = {
        "task_id": task_id,
        "status": "pending",
        "user_id": user_id,
        "message": "Email verification in progress",
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": None
    }
    
    # Add background task for async processing
    background_tasks.add_task(send_verification_email_task, user_id, task_id)
    
    return {
        "message": "Email verification started",
        "task_id": task_id,
        "status": "pending",
        "status_url": status_url,
        "_links": {
            "self": {
                "href": status_url,
                "method": "GET"
            },
            "user": {
                "href": f"{base_url}/api/v1/users/{user_id}",
                "method": "GET"
            }
        }
    }


@router.get("/tasks/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str, request: Request):
    """
    Poll endpoint to check async task status
    
    Features:
    - Status polling for async operations
    - HATEOAS links
    
    Status values:
    - pending: Task is queued
    - processing: Task is being processed
    - completed: Task finished successfully
    - failed: Task failed
    
    - **task_id**: The ID of the task to check
    
    Returns:
    - 200: Task status
    - 404: Task not found
    """
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = task_storage[task_id].copy()
    
    # Add HATEOAS links
    base_url = str(request.base_url).rstrip('/')
    task["_links"] = {
        "self": {
            "href": f"{base_url}/api/v1/users/tasks/{task_id}",
            "method": "GET"
        }
    }
    
    if task.get("user_id"):
        task["_links"]["user"] = {
            "href": f"{base_url}/api/v1/users/{task['user_id']}",
            "method": "GET"
        }
    
    return task


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
    if user_id not in MOCK_USERS:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Mock rental data
    return []


@router.get("/{user_id}/rentals/{rental_id}")
async def get_user_rental_details(user_id: int, rental_id: int):
    """
    Get detailed information about a specific rental
    
    - **user_id**: The ID of the user
    - **rental_id**: The ID of the rental
    """
    if user_id not in MOCK_USERS:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "message": "NOT IMPLEMENTED",
        "user_id": user_id,
        "rental_id": rental_id
    }

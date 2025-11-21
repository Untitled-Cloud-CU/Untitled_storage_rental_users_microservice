"""
Data models for Users Service - Enhanced with HATEOAS
Defines the structure of User resources
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict
from datetime import datetime
from enum import Enum


class UserStatus(str, Enum):
    """User account status"""
    active = "active"
    inactive = "inactive"
    suspended = "suspended"


class UserBase(BaseModel):
    """Base user model with common fields"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=2)
    zip_code: Optional[str] = Field(None, max_length=10)


class UserCreate(UserBase):
    """Model for creating a new user"""
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        return v


class UserUpdate(BaseModel):
    """Model for updating user information"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    state: Optional[str] = Field(None, max_length=2)
    zip_code: Optional[str] = Field(None, max_length=10)


class User(UserBase):
    """Complete user model with all fields - Enhanced with HATEOAS"""
    user_id: int
    status: UserStatus = UserStatus.active
    created_at: datetime
    updated_at: datetime
    _links: Optional[Dict[str, dict]] = None  # HATEOAS links

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Model for login requests"""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Model for login response"""
    user_id: int
    email: str
    token: str
    token_type: str = "bearer"
    message: str


class UserRental(BaseModel):
    """Model for user rental information"""
    rental_id: int
    unit_id: int
    facility_name: str
    unit_number: str
    start_date: str
    end_date: Optional[str] = None
    monthly_rate: float
    is_active: bool


# NEW: Async Task Models for 202 Accepted
class TaskStatus(BaseModel):
    """Model for async task status"""
    task_id: str
    status: str  # pending, processing, completed, failed
    user_id: Optional[int] = None
    message: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    _links: Optional[Dict[str, dict]] = None


class TaskCreate(BaseModel):
    """Model for task creation response (202 Accepted)"""
    message: str
    task_id: str
    status: str
    status_url: str
    _links: Optional[Dict[str, dict]] = None

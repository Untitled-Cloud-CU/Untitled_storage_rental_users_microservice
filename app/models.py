"""
Data models for Users Service
Defines the structure of User resources
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


class UserStatus(str, Enum):
    """User account status"""
    active = "active"
    inactive = "inactive"
    suspended = "suspended"


class UserBase(BaseModel):
    """Base user model with common fields"""
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None


class UserCreate(UserBase):
    """Model for creating a new user"""
    password: str


class UserUpdate(BaseModel):
    """Model for updating user information"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None


class User(UserBase):
    """Complete user model with all fields"""
    user_id: int
    status: UserStatus = UserStatus.active
    created_at: datetime
    updated_at: datetime

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

"""
User Schemas
Pydantic models for user-related data validation.
"""

from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID
from typing import Optional


class UserSignup(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str
    display_name: Optional[str] = None


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserProfile(BaseModel):
    """Schema for user profile response."""
    id: UUID
    email: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime


class AuthResponse(BaseModel):
    """Schema for authentication response."""
    access_token: str
    refresh_token: str
    user: UserProfile


class TokenData(BaseModel):
    """Schema for decoded JWT token data."""
    user_id: str
    email: Optional[str] = None

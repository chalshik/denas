from pydantic import BaseModel, EmailStr
from typing import Optional
from app.schemas.user import User, UserRole


class UserRegistrationRequest(BaseModel):
    """User registration request schema"""
    email: EmailStr


class UserStatsResponse(BaseModel):
    """User statistics response schema"""
    total_users: int
    regular_users: int
    total_admins: int
    new_users_this_month: int
    active_users: int


class UserListResponse(BaseModel):
    """User list response with pagination"""
    users: list[User]
    total_count: int
    page: int
    limit: int
    has_next: bool
    has_previous: bool


class AuthRequest(BaseModel):
    """Base authentication request schema"""
    email: EmailStr


class LoginRequest(AuthRequest):
    """User login request schema"""
    pass


class AuthResponse(BaseModel):
    """Authentication response schema"""
    success: bool
    message: str
    user: Optional[User] = None
    is_new_user: Optional[bool] = False
    access_token_info: Optional[dict] = None


class ProfileUpdateRequest(BaseModel):
    """Profile update request schema"""
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None


class TokenInfo(BaseModel):
    """Firebase token information"""
    uid: str
    email: Optional[str] = None
    email_verified: Optional[bool] = False
    name: Optional[str] = None
    picture: Optional[str] = None 
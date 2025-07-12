from pydantic import BaseModel, Field, field_validator
from typing import Optional
from app.schemas.user import User, UserRole, validate_phone


class UserRegistrationRequest(BaseModel):
    """User registration request schema"""
    phone: str = Field(..., description="Phone number in international format")
    
    @field_validator('phone')
    @classmethod
    def validate_phone_field(cls, v):
        return validate_phone(v)


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
    phone: str = Field(..., description="Phone number in international format")
    
    @field_validator('phone')
    @classmethod
    def validate_phone_field(cls, v):
        return validate_phone(v)


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
    phone: Optional[str] = Field(None, description="Phone number in international format")
    role: Optional[UserRole] = None
    
    @field_validator('phone')
    @classmethod
    def validate_phone_field(cls, v):
        if v is not None:
            return validate_phone(v)
        return v


class TokenInfo(BaseModel):
    """Firebase token information"""
    uid: str
    phone: Optional[str] = None
    phone_verified: Optional[bool] = False
    name: Optional[str] = None
    picture: Optional[str] = None 
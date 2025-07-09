from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from app.models.user import UserType

class UserResponse(BaseModel):
    id: int
    firebase_uid: str
    phone: str
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    user_type: UserType
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    """Response schema for listing users in admin panel"""
    id: int
    firebase_uid: str
    phone: str
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    user_type: UserType
    created_at: str
    updated_at: str
    
    # Additional computed fields for admin
    display_name: Optional[str] = None
    is_admin: bool = False
    
    class Config:
        from_attributes = True
    
    @validator('display_name', always=True)
    def compute_display_name(cls, v, values):
        """Compute display name from first_name and last_name"""
        first = values.get('first_name', '')
        last = values.get('last_name', '')
        
        if first and last:
            return f"{first} {last}"
        elif first:
            return first
        elif last:
            return last
        else:
            return values.get('phone', 'Unknown User')
    
    @validator('is_admin', always=True)
    def compute_is_admin(cls, v, values):
        """Check if user is admin or superadmin"""
        user_type = values.get('user_type')
        return user_type in [UserType.ADMIN, UserType.SUPERADMIN]

class UserCreateRequest(BaseModel):
    """Schema for creating a new user (admin only)"""
    firebase_uid: str = Field(..., description="Firebase UID")
    phone: str = Field(..., description="Phone number")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    email: Optional[str] = Field(None, description="Email address")
    user_type: UserType = Field(UserType.USER, description="User type")
    
    @validator('user_type')
    def validate_user_type(cls, v):
        """Only allow creating certain user types"""
        if v not in [UserType.USER, UserType.VENDOR, UserType.ADMIN]:
            raise ValueError('Cannot create SUPERADMIN users through API')
        return v

class UserUpdateRequest(BaseModel):
    """Schema for updating user information (admin only)"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    user_type: Optional[UserType] = None
    
    @validator('user_type')
    def validate_user_type(cls, v):
        """Validate user type changes"""
        if v is not None and v not in [UserType.USER, UserType.VENDOR, UserType.ADMIN]:
            raise ValueError('Cannot set user type to SUPERADMIN through API')
        return v

class UserStatusUpdate(BaseModel):
    """Schema for updating user status"""
    user_type: UserType
    
class UserStats(BaseModel):
    """Schema for user statistics in admin dashboard"""
    total_users: int
    total_vendors: int
    total_admins: int
    active_users: int
    pending_vendors: int
    approved_vendors: int
    rejected_vendors: int
    
class UsersListResponse(BaseModel):
    """Paginated response for users list"""
    users: List[UserListResponse]
    total: int
    page: int
    per_page: int
    total_pages: int 
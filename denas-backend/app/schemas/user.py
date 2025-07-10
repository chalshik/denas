from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import enum
import re


class UserRole(enum.Enum):
    USER = "User"
    ADMIN = "Admin"
    MANAGER = "Manager"


def validate_phone(phone: str) -> str:
    """Validate phone number format"""
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Check if it's a valid international format
    if not re.match(r'^\+?[1-9]\d{1,14}$', cleaned):
        raise ValueError('Invalid phone number format')
    
    return cleaned


class UserBase(BaseModel):
    uid: str
    phone: str = Field(..., description="Phone number in international format")
    role: UserRole = UserRole.USER
    
    @field_validator('phone')
    @classmethod
    def validate_phone_field(cls, v):
        return validate_phone(v)


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    uid: Optional[str] = None
    phone: Optional[str] = Field(None, description="Phone number in international format")
    role: Optional[UserRole] = None
    
    @field_validator('phone')
    @classmethod
    def validate_phone_field(cls, v):
        if v is not None:
            return validate_phone(v)
        return v


class UserInDB(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserWithDetails(User):
    orders: Optional[list] = []
    favorites: Optional[list] = []
    shopping_cart: Optional[dict] = None

    class Config:
        from_attributes = True 
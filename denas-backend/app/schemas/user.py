from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import enum


class UserRole(enum.Enum):
    USER = "User"
    ADMIN = "Admin"
    MANAGER = "Manager"


class UserBase(BaseModel):
    uid: str
    email: EmailStr
    role: UserRole = UserRole.USER


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    uid: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None


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
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.services.firebase import get_current_user_uid, get_current_user_uid_optional
from app.services.user_auth import UserService
from app.models.user import User, UserRole

async def get_current_user(
    firebase_uid: str = Depends(get_current_user_uid),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from database
    Raises 404 if user not found (user needs to be registered first)
    """
    user = await UserService.get_user_by_uid(db, firebase_uid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Please complete registration first."
        )
    return user

async def get_current_user_optional(
    firebase_uid: Optional[str] = Depends(get_current_user_uid_optional),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current authenticated user from database (optional)
    Returns None if no token provided or user not found
    """
    if not firebase_uid:
        return None
    
    user = await UserService.get_user_by_uid(db, firebase_uid)
    return user

async def require_admin_access(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require admin or manager role
    Returns current user if authorized, raises 403 otherwise
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

async def require_manager_access(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require manager or admin role
    Returns current user if authorized, raises 403 otherwise
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required"
        )
    return current_user 
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.db.database import get_db
from app.services.firebase import get_current_user_uid
from app.services.user_auth import UserService
from app.api.dependencies import get_current_user, require_admin_access
from app.schemas.auth import (
    UserRegistrationRequest, 
    UserStatsResponse, 
    UserListResponse
)
from app.schemas.user import User, UserRole
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", response_model=User)
async def register_user(
    request: UserRegistrationRequest,
    firebase_uid: str = Depends(get_current_user_uid),
    db: Session = Depends(get_db)
):
    """
    Register a new user with Firebase UID and email
    The Firebase token provides the UID, email comes from request body
    """
    try:
        user = await UserService.create_user(
            db=db,
            uid=firebase_uid,
            email=request.email
        )
        
        logger.info(f"User registered successfully: {user.id} with UID: {firebase_uid}")
        return user
        
    except Exception as e:
        if "already exists" in str(e).lower() or "unique" in str(e).lower():
            # User already exists, return existing user
            existing_user = await UserService.get_user_by_uid(db, firebase_uid)
            if existing_user:
                logger.info(f"User already registered: {existing_user.id} with UID: {firebase_uid}")
                return existing_user
            
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed"
        )


@router.get("/me", response_model=User)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's profile
    """
    return current_user


@router.get("/me/or-create", response_model=User)
async def get_or_create_user(
    firebase_uid: str = Depends(get_current_user_uid),
    db: Session = Depends(get_db)
):
    """
    Get current user or create if doesn't exist
    This endpoint handles the auth flow for existing Firebase users
    """
    try:
        # Try to get user first
        user = await UserService.get_user_by_uid(db, firebase_uid)
        if user:
            logger.info(f"Existing user found: {user.id} with UID: {firebase_uid}")
            return user
        
        # User doesn't exist, we need email to create
        # In this case, the frontend should call /register with email
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Please complete registration first."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get or create user error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )


# Admin endpoints
@router.get("/admin/users", response_model=UserListResponse)
async def get_all_users(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    role_filter: Optional[UserRole] = Query(None),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_access)
):
    """
    Get all users (Admin only) with pagination and filtering
    """
    try:
        offset = (page - 1) * limit
        users, total_count = await UserService.get_all_users(
            db=db,
            limit=limit,
            offset=offset,
            role_filter=role_filter
        )
        
        return UserListResponse(
            users=users,
            total_count=total_count,
            page=page,
            limit=limit,
            has_next=(offset + limit) < total_count,
            has_previous=page > 1
        )
        
    except Exception as e:
        logger.error(f"Get all users error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get users"
        )


@router.get("/admin/stats", response_model=UserStatsResponse)
async def get_user_statistics(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_access)
):
    """
    Get user statistics (Admin only)
    """
    try:
        stats = await UserService.get_user_stats(db)
        return UserStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Get user stats error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user statistics"
        )


@router.put("/admin/users/{user_id}/role", response_model=User)
async def update_user_role(
    user_id: int,
    new_role: UserRole,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_access)
):
    """
    Update user role (Admin only)
    """
    try:
        updated_user = await UserService.update_user_role(
            db=db,
            user_id=user_id,
            new_role=new_role
        )
        
        logger.info(f"User role updated by admin {admin_user.id}: user {user_id} -> {new_role}")
        return updated_user
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Update user role error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user role"
        )


@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_access)
):
    """
    Delete user (Admin only)
    """
    try:
        await UserService.delete_user(db, user_id)
        
        logger.info(f"User deleted by admin {admin_user.id}: user {user_id}")
        return {"success": True, "message": "User deleted successfully"}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Delete user error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )


@router.get("/admin/users/search", response_model=List[User])
async def search_users(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_access)
):
    """
    Search users by email or UID (Admin only)
    """
    try:
        users = await UserService.search_users(
            db=db,
            search_term=q,
            limit=limit
        )
        return users
        
    except Exception as e:
        logger.error(f"Search users error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search users"
        ) 
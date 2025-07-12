from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List

from app.db.database import get_db
from app.services.firebase import FirebaseService
from app.services.user_auth import UserService
from app.api.dependencies import get_current_user, require_admin_access
from app.schemas.auth import (
    UserRegistrationRequest,
    UserLoginRequest,
    TokenResponse,
    UserStatsResponse, 
    UserListResponse
)
from app.schemas.user import User, UserRole
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    request: UserRegistrationRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user with a phone number and password.
    Creates a user in Firebase and the local database.
    Returns a custom Firebase token for client-side login.
    """
    # Check if user already exists in local DB
    existing_user = await UserService.get_user_by_phone(db, request.phone)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this phone number already exists."
        )

    try:
        # 1. Create user in Firebase
        firebase_uid = await FirebaseService.create_user_with_phone(request.phone)
        
        # 2. Create user in local database
        await UserService.create_user(
            db=db,
            uid=firebase_uid,
            phone=request.phone,
            password=request.password
        )
        
        # 3. Create a custom token for the new user
        custom_token = await FirebaseService.create_custom_token(firebase_uid)
        
        logger.info(f"User registered successfully with UID: {firebase_uid}")
        return TokenResponse(firebase_token=custom_token)
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed due to a database conflict. This may be a race condition."
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Registration error: {str(e)}")
        # Potentially delete the firebase user if DB registration fails
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration."
        )

@router.post("/login", response_model=TokenResponse)
async def login_for_token(
    request: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate a user with phone and password.
    Returns a custom Firebase token for client-side login.
    """
    user = await UserService.verify_user(db, phone=request.phone, password=request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create a custom token for the user
    custom_token = await FirebaseService.create_custom_token(user.uid)
    return TokenResponse(firebase_token=custom_token)


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
        
        # User doesn't exist, we need phone number to create
        # In this case, the frontend should call /register with phone
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
    """Search users by phone or UID (admin only)"""
    try:
        users = await UserService.search_users(db, q, limit)
        return users
        
    except Exception as e:
        logger.error(f"Search users error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search users"
        ) 
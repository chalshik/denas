from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from app.db.database import get_db
from app.schemas.user import User, UserCreate, UserUpdate, UserWithDetails
from app.models.user import User as UserModel, UserRole
from app.api.dependencies import get_current_user, require_admin_access
from app.services.user_auth import UserService

router = APIRouter()

# User endpoints
@router.get("/me", response_model=User)
async def get_my_profile(
    current_user: UserModel = Depends(get_current_user)
):
    """Get current user's profile"""
    return current_user


@router.get("/me/details", response_model=UserWithDetails)
async def get_my_profile_with_details(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's profile with orders, favorites, and cart"""
    user_with_details = db.query(UserModel).options(
        joinedload(UserModel.orders),
        joinedload(UserModel.favorites),
        joinedload(UserModel.shopping_cart)
    ).filter(UserModel.id == current_user.id).first()
    
    return user_with_details


@router.put("/me", response_model=User)
async def update_my_profile(
    user_update: UserUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile (limited fields)"""
    try:
        # Users can only update their own email (role changes require admin)
        if user_update.role is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot change your own role"
            )
        
        if user_update.uid is not None and user_update.uid != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot change your UID"
            )
        
        # Update allowed fields
        if user_update.email is not None:
            # Check if email is already taken by another user
            existing_user = db.query(UserModel).filter(
                UserModel.email == user_update.email,
                UserModel.id != current_user.id
            ).first()
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            current_user.email = user_update.email
        
        db.commit()
        db.refresh(current_user)
        return current_user
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


# Admin endpoints
@router.get("/", response_model=List[User])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    role_filter: Optional[UserRole] = Query(None),
    admin_user: UserModel = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Get all users with filtering (admin only)"""
    try:
        users, _ = await UserService.get_all_users(
            db=db,
            limit=limit,
            offset=skip,
            role_filter=role_filter
        )
        return users
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users"
        )


@router.get("/{user_id}", response_model=UserWithDetails)
async def get_user_by_id(
    user_id: int,
    admin_user: UserModel = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Get user by ID with details (admin only)"""
    try:
        user = db.query(UserModel).options(
            joinedload(UserModel.orders),
            joinedload(UserModel.favorites),
            joinedload(UserModel.shopping_cart)
        ).filter(UserModel.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user"
        )


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    admin_user: UserModel = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Update user (admin only)"""
    try:
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if email is already taken (if being updated)
        if user_update.email and user_update.email != user.email:
            existing_user = await UserService.get_user_by_email(db, user_update.email)
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Update fields
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    admin_user: UserModel = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Delete user (admin only)"""
    try:
        await UserService.delete_user(db, user_id)
        return {"success": True, "message": "User deleted successfully"}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )


@router.get("/search/{search_term}", response_model=List[User])
async def search_users(
    search_term: str,
    limit: int = Query(50, ge=1, le=100),
    admin_user: UserModel = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Search users by email or UID (admin only)"""
    try:
        users = await UserService.search_users(
            db=db,
            search_term=search_term,
            limit=limit
        )
        return users
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search users"
        ) 
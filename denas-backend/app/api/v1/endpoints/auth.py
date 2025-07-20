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
    Register a new user with Firebase UID and phone number
    The Firebase token provides the UID, phone comes from request body
    """
    try:
        user = await UserService.create_user(
            db=db,
            uid=firebase_uid,
            phone=request.phone
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
        deleted_user = await UserService.delete_user(db=db, user_id=user_id)
        
        logger.info(f"User deleted by admin {admin_user.id}: user {user_id}")
        return {
            "success": True,
            "message": f"User {user_id} deleted successfully",
            "deleted_user": deleted_user
        }
        
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
    Search users by phone number or other criteria (Admin only)
    """
    try:
        users = await UserService.search_users(
            db=db,
            search_term=q,
            limit=limit
        )
        
        logger.info(f"User search performed by admin {admin_user.id}: '{q}' -> {len(users)} results")
        return users
        
    except Exception as e:
        logger.error(f"Search users error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search users"
        )


# New cookie-based authentication endpoints
from fastapi import Response, Request
from app.schemas.auth import TokenData, RefreshTokenRequest, TokenResponse, SessionResponse
import requests
import json
import os

@router.post("/set-cookie", response_model=TokenResponse)
async def set_authentication_cookies(
    response: Response,
    token_data: TokenData,
    db: Session = Depends(get_db)
):
    """
    Set authentication cookies after successful login
    """
    try:
        # Validate the ID token first
        from app.services.firebase import FirebaseService
        firebase_service = FirebaseService()
        
        # Verify the token and get user info
        firebase_uid = await firebase_service.verify_token_direct(token_data.id_token)
        
        # Set httpOnly cookies
        response.set_cookie(
            key="id_token",
            value=token_data.id_token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=604800  # 1 week (7 days)
        )
        
        response.set_cookie(
            key="refresh_token",
            value=token_data.refresh_token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=2592000  # 30 days
        )
        
        logger.info(f"Authentication cookies set for user: {firebase_uid}")
        
        return TokenResponse(
            success=True,
            message="Authentication cookies set successfully",
            expires_in=604800  # 1 week (7 days)
        )
        
    except Exception as e:
        logger.error(f"Set cookie error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to set authentication cookies"
        )


@router.post("/refresh-token", response_model=TokenResponse)
async def refresh_authentication_token(
    request: Request,
    response: Response
):
    """
    Refresh the authentication token using refresh token from cookies
    """
    try:
        # Get refresh token from cookies
        refresh_token = request.cookies.get("refresh_token")
        
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No refresh token found"
            )
        
        # Make request to Firebase to refresh token
        from app.core.config import settings
        
        if not settings.FIREBASE_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Firebase configuration error"
            )
        
        refresh_url = f"https://securetoken.googleapis.com/v1/token?key={settings.FIREBASE_API_KEY}"
        
        refresh_payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        
        refresh_response = requests.post(
            refresh_url,
            data=refresh_payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if refresh_response.status_code != 200:
            logger.error(f"Token refresh failed: {refresh_response.text}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token refresh failed"
            )
        
        refresh_data = refresh_response.json()
        new_id_token = refresh_data.get("id_token")
        new_refresh_token = refresh_data.get("refresh_token")
        expires_in = int(refresh_data.get("expires_in", 3600))
        
        # Update cookies with new tokens
        response.set_cookie(
            key="id_token",
            value=new_id_token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=604800  # 1 week (7 days)
        )
        
        if new_refresh_token:
            response.set_cookie(
                key="refresh_token",
                value=new_refresh_token,
                httponly=True,
                secure=True,
                samesite="strict",
                max_age=2592000  # 30 days
            )
        
        logger.info("Token refreshed successfully")
        
        return TokenResponse(
            success=True,
            message="Token refreshed successfully",
            expires_in=604800  # 1 week (7 days)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token"
        )


@router.post("/logout", response_model=TokenResponse)
async def logout_user(response: Response):
    """
    Logout user by clearing authentication cookies
    """
    try:
        # Clear cookies
        response.delete_cookie(key="id_token")
        response.delete_cookie(key="refresh_token")
        
        logger.info("User logged out - cookies cleared")
        
        return TokenResponse(
            success=True,
            message="Logged out successfully"
        )
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to logout"
        )


@router.get("/session", response_model=SessionResponse)
async def check_session(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Check if user has a valid session
    """
    try:
        # Get ID token from cookies
        id_token = request.cookies.get("id_token")
        
        if not id_token:
            return SessionResponse(
                success=True,
                authenticated=False,
                message="No session found"
            )
        
        # Verify the token
        from app.services.firebase import FirebaseService
        firebase_service = FirebaseService()
        
        try:
            firebase_uid = await firebase_service.verify_token_direct(id_token)
            
            # Get user from database
            user = await UserService.get_user_by_uid(db, firebase_uid)
            
            if user:
                return SessionResponse(
                    success=True,
                    authenticated=True,
                    user=user,
                    message="Session valid"
                )
            else:
                return SessionResponse(
                    success=True,
                    authenticated=False,
                    message="User not found in database"
                )
                
        except Exception as token_error:
            logger.error(f"Token validation error: {str(token_error)}")
            return SessionResponse(
                success=True,
                authenticated=False,
                message="Invalid session"
            )
        
    except Exception as e:
        logger.error(f"Session check error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check session"
        ) 
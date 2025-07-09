from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.schemas.vendor import VendorProfileResponse
from app.schemas.user import UserListResponse, UserUpdateRequest, UserStats, UsersListResponse
from app.schemas.product import ProductResponse, ProductResponseSpecific, ProductStatus
from app.schemas.admin import AdminDashboardStats, UserStats, VendorStats, ProductStats
from app.services.auth_service import AuthService
from app.services.product_service import ProductService
from app.services.vendor_service import VendorService
from app.services.firebase_service import FirebaseService
from app.middleware.firebase_auth import (
    get_current_user_with_role, 
    require_superadmin_role,
    require_admin_or_superadmin_role,
    check_admin_permission
)
from app.models.user import User, UserType
from app.models.vendor_profile import VendorProfile, VendorStatus
from app.models.product import Product
import logging
from typing import List, Optional
from pydantic import BaseModel
import math

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])

class VendorStatusUpdate(BaseModel):
    status: VendorStatus
    reject_reason: Optional[str] = None

class VendorRejectRequest(BaseModel):
    reject_reason: Optional[str] = None

class ProductStatusUpdate(BaseModel):
    status: ProductStatus

class UserTypeUpdate(BaseModel):
    user_type: UserType

# Pagination wrapper for products
class ProductsListResponse(BaseModel):
    products: List[ProductResponseSpecific]
    total: int
    page: int
    per_page: int
    total_pages: int

# Pagination wrapper for vendors
class VendorsListResponse(BaseModel):
    vendors: List[VendorProfileResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

# Enhanced admin role checkers
require_user_management = check_admin_permission("can_manage_users")
require_vendor_management = check_admin_permission("can_manage_vendors") 
require_product_management = check_admin_permission("can_manage_products")

# ========================================
# DASHBOARD & STATS ENDPOINTS
# ========================================

@router.get("/stats/users", response_model=UserStats)
async def get_user_stats(
    db: Session = Depends(get_db),
    user_data: tuple = Depends(require_admin_or_superadmin_role)
):
    stats = await AuthService.get_user_stats(db)
    return UserStats(**stats)

@router.get("/stats/vendors", response_model=VendorStats)
async def get_vendor_stats(
    db: Session = Depends(get_db),
    user_data: tuple = Depends(require_admin_or_superadmin_role)
):
    stats = await VendorService.get_vendor_stats(db)
    return VendorStats(**stats)

@router.get("/stats/products", response_model=ProductStats)
async def get_product_stats(
    db: Session = Depends(get_db),
    user_data: tuple = Depends(require_admin_or_superadmin_role)
):
    product_service = ProductService(db)
    stats = product_service.get_product_stats()
    return ProductStats(**stats)

@router.get("/dashboard", response_model=AdminDashboardStats)
async def get_admin_dashboard(
    db: Session = Depends(get_db),
    user_data: tuple = Depends(require_admin_or_superadmin_role)
):
    """
    Get admin dashboard statistics (requires ADMIN or SUPERADMIN role)
    """
    try:
        # Get user statistics
        user_stats_data = await AuthService.get_user_stats(db)
        
        # Get vendor statistics
        vendor_stats_data = await VendorService.get_vendor_stats(db)

        # Get product statistics
        product_service = ProductService(db)
        product_stats_data = product_service.get_product_stats()
        
        return AdminDashboardStats(
            users=UserStats(**user_stats_data),
            products=ProductStats(**product_stats_data),
            vendors=VendorStats(**vendor_stats_data)
        )
        
    except Exception as e:
        logger.error(f"Error getting admin dashboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get dashboard data"
        )

# ========================================
# USER MANAGEMENT ENDPOINTS
# ========================================

@router.get("/users", response_model=UsersListResponse)
async def get_all_users(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    user_type: Optional[UserType] = Query(None, description="Filter by user type"),
    search: Optional[str] = Query(None, description="Search by phone, email, or name"),
    db: Session = Depends(get_db),
    user_data: tuple = Depends(require_user_management)
):
    """
    Get all users with pagination and filtering (requires user management permission)
    """
    try:
        offset = (page - 1) * per_page
        
        if search:
            # Search users
            users = await AuthService.search_users(db, search, limit=per_page)
            total = len(users)  # For search, we'll use the returned count
        else:
            # Get users with pagination
            users, total = await AuthService.get_all_users(
                db, 
                limit=per_page, 
                offset=offset, 
                user_type_filter=user_type
            )
        
        # Convert to response format
        user_list = []
        for user in users:
            user_response = UserListResponse(
                id=user.id,
                firebase_uid=user.firebase_uid,
                phone=user.phone,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                user_type=user.user_type,
                created_at=user.created_at.isoformat(),
                updated_at=user.updated_at.isoformat()
            )
            user_list.append(user_response)
        
        total_pages = math.ceil(total / per_page)
        
        return UsersListResponse(
            users=user_list,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get users"
        )

@router.get("/users/{user_id}", response_model=UserListResponse)
async def get_user_details(
    user_id: int,
    db: Session = Depends(get_db),
    user_data: tuple = Depends(require_user_management)
):
    """
    Get user details by ID (requires user management permission)
    """
    try:
        user = await AuthService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserListResponse(
            id=user.id,
            firebase_uid=user.firebase_uid,
            phone=user.phone,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            user_type=user.user_type,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user details"
        )

@router.patch("/users/{user_id}/type")
async def update_user_type(
    user_id: int,
    type_update: UserTypeUpdate,
    db: Session = Depends(get_db),
    user_data: tuple = Depends(require_user_management)
):
    """
    Update user type (requires user management permission - SUPERADMIN only)
    """
    try:
        success, message, user = await AuthService.update_user_type(
            db, user_id, type_update.user_type
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        # Update Firebase claims
        firebase_success, firebase_message = await FirebaseService.set_user_role(
            user.firebase_uid, 
            type_update.user_type.value
        )
        
        if not firebase_success:
            logger.warning(f"Failed to update Firebase claims: {firebase_message}")
        
        return {
            "success": True,
            "message": message,
            "user_id": user_id,
            "new_type": type_update.user_type.value,
            "firebase_updated": firebase_success
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user type: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user type"
        )

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    user_data: tuple = Depends(require_user_management)
):
    """
    Delete user (requires user management permission - SUPERADMIN only)
    """
    try:
        success, message = await AuthService.delete_user(db, user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        return {
            "success": True,
            "message": message,
            "user_id": user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )

# ========================================
# PRODUCT MANAGEMENT ENDPOINTS
# ========================================

@router.get("/products", response_model=ProductsListResponse)
async def get_all_products(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    vendor_id: Optional[int] = Query(None, description="Filter by vendor ID"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    db: Session = Depends(get_db),
    user_data: tuple = Depends(require_product_management)
):
    """
    Get all products with filtering and pagination (requires product management permission)
    Returns comprehensive product data with vendor_profile, variations, characteristics, etc.
    """
    try:
        offset = (page - 1) * per_page
        
        service = ProductService(db)
        products, total = service.get_all_for_admin(
            status_filter=status_filter,
            vendor_id=vendor_id,
            category_id=category_id,
            limit=per_page,
            offset=offset
        )
        
        total_pages = math.ceil(total / per_page) if total > 0 else 1
        
        return ProductsListResponse(
            products=products,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Error getting products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get products"
        )

@router.get("/products/pending", response_model=ProductsListResponse)
async def get_pending_products(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    user_data: tuple = Depends(require_product_management)
):
    """
    Get pending products for review (requires product management permission)
    Returns comprehensive product data with vendor_profile, variations, characteristics, etc.
    """
    try:
        offset = (page - 1) * per_page
        
        service = ProductService(db)
        products = service.get_pending_products(limit=per_page, offset=offset)
        
        # Get total count of pending products for pagination
        total = service.get_pending_products_count()
        total_pages = math.ceil(total / per_page) if total > 0 else 1
        
        return ProductsListResponse(
            products=products,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Error getting pending products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get pending products"
        )

@router.get("/products/{product_id}", response_model=ProductResponseSpecific)
async def get_product_details(
    product_id: int,
    db: Session = Depends(get_db),
    user_data: tuple = Depends(require_product_management)
):
    """
    Get product details by ID (requires product management permission)
    Returns comprehensive product data with vendor_profile, variations, characteristics, etc.
    """
    try:
        service = ProductService(db)
        product = service.get(product_id)
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        return product
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get product details"
        )

@router.patch("/products/{product_id}/status")
async def update_product_status(
    product_id: int,
    status_update: ProductStatusUpdate,
    db: Session = Depends(get_db),
    user_data: tuple = Depends(require_product_management)
):
    """
    Update product status (requires product management permission)
    """
    try:
        service = ProductService(db)
        product = service.update_product_status(product_id, status_update.status.value)
        
        logger.info(f"Product {product_id} status updated to {status_update.status.value}")
        
        return {
            "success": True,
            "message": f"Product status updated to {status_update.status.value}",
            "product_id": product_id,
            "new_status": status_update.status.value
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating product status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update product status"
        )

@router.post("/products/{product_id}/approve")
async def approve_product(
    product_id: int,
    db: Session = Depends(get_db),
    user_data: tuple = Depends(require_product_management)
):
    """
    Approve product (shortcut for updating status to approved)
    """
    status_update = ProductStatusUpdate(status=ProductStatus.approved)
    return await update_product_status(product_id, status_update, db, user_data)

@router.post("/products/{product_id}/reject")
async def reject_product(
    product_id: int,
    db: Session = Depends(get_db),
    user_data: tuple = Depends(require_product_management)
):
    """
    Reject product (shortcut for updating status to rejected)
    """
    status_update = ProductStatusUpdate(status=ProductStatus.rejected)
    return await update_product_status(product_id, status_update, db, user_data)

@router.delete("/products/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    user_data: tuple = Depends(require_product_management)
):
    """
    Delete product (requires product management permission)
    """
    try:
        service = ProductService(db)
        result = service.delete_for_admin(product_id)
        
        return {
            "success": True,
            "message": result["message"],
            "product_id": product_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete product"
        )

# ========================================
# EXISTING VENDOR MANAGEMENT ENDPOINTS
# (Keep all existing vendor endpoints as they are)
# ========================================

@router.get("/vendors", response_model=VendorsListResponse)
async def get_all_vendors(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search by business name, organization name, or INN"),
    db: Session = Depends(get_db),
    user_data: tuple = Depends(require_vendor_management)
):
    """
    Get all vendor profiles with pagination and filtering (requires ADMIN or SUPERADMIN role)
    """
    try:
        offset = (page - 1) * per_page
        
        # Build query
        query = db.query(VendorProfile)
        
        # Apply status filter
        if status:
            query = query.filter(VendorProfile.status == status)
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    VendorProfile.business_name.ilike(search_term),
                    VendorProfile.organization_name.ilike(search_term),
                    VendorProfile.inn.ilike(search_term)
                )
            )
        
        # Get total count
        total = query.count()
        total_pages = math.ceil(total / per_page) if total > 0 else 1
        
        # Apply pagination
        vendor_profiles = query.offset(offset).limit(per_page).all()
        
        vendors_list = [
            VendorProfileResponse(
                id=vp.id,
                user_id=vp.user_id,
                business_type=vp.business_type,
                business_name=vp.business_name,
                organization_name=vp.organization_name,
                legal_form=vp.legal_form,
                inn=vp.inn,
                registration_country=vp.registration_country,
                registration_date=vp.registration_date,
                passport_front_url=vp.passport_front_url,
                passport_back_url=vp.passport_back_url,
                status=vp.status,
                created_at=vp.created_at.isoformat(),
                description=vp.description,
                reject_reason=vp.reject_reason
            )
            for vp in vendor_profiles
        ]
        
        return VendorsListResponse(
            vendors=vendors_list,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Error getting all vendors: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get vendors"
        )

@router.get("/vendors/pending", response_model=List[VendorProfileResponse])
async def get_pending_vendors(
    db: Session = Depends(get_db),
    user_data: tuple = Depends(require_vendor_management)
):
    """
    Get pending vendor applications (requires vendor management permission)
    """
    try:
        pending_vendors = db.query(VendorProfile).filter(
            VendorProfile.status == VendorStatus.PENDING
        ).all()
        
        return [
            VendorProfileResponse(
                id=vp.id,
                user_id=vp.user_id,
                business_type=vp.business_type,
                business_name=vp.business_name,
                organization_name=vp.organization_name,
                legal_form=vp.legal_form,
                inn=vp.inn,
                registration_country=vp.registration_country,
                registration_date=vp.registration_date,
                passport_front_url=vp.passport_front_url,
                passport_back_url=vp.passport_back_url,
                status=vp.status,
                created_at=vp.created_at.isoformat(),
                description=vp.description,
                reject_reason=vp.reject_reason
            )
            for vp in pending_vendors
        ]
        
    except Exception as e:
        logger.error(f"Error getting pending vendors: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get pending vendors"
        )

@router.get("/vendors/{vendor_id}", response_model=VendorProfileResponse)
async def get_vendor_details(
    vendor_id: int,
    db: Session = Depends(get_db),
    user_data: tuple = Depends(require_vendor_management)
):
    """
    Get vendor details by ID (requires vendor management permission)
    """
    try:
        vendor_profile = db.query(VendorProfile).filter(VendorProfile.id == vendor_id).first()
        if not vendor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found"
            )
        
        return VendorProfileResponse(
            id=vendor_profile.id,
            user_id=vendor_profile.user_id,
            business_type=vendor_profile.business_type,
            business_name=vendor_profile.business_name,
            organization_name=vendor_profile.organization_name,
            legal_form=vendor_profile.legal_form,
            inn=vendor_profile.inn,
            registration_country=vendor_profile.registration_country,
            registration_date=vendor_profile.registration_date,
            passport_front_url=vendor_profile.passport_front_url,
            passport_back_url=vendor_profile.passport_back_url,
            status=vendor_profile.status,
            created_at=vendor_profile.created_at.isoformat(),
            description=vendor_profile.description,
            reject_reason=vendor_profile.reject_reason
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting vendor details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get vendor details"
        )

@router.patch("/vendors/{vendor_id}/status")
async def update_vendor_status(
    vendor_id: int,
    status_update: VendorStatusUpdate,
    db: Session = Depends(get_db),
    user_data: tuple = Depends(require_vendor_management)
):
    """
    Update vendor status (requires ADMIN or SUPERADMIN role)
    """
    try:
        # Get vendor profile
        vendor_profile = db.query(VendorProfile).filter(VendorProfile.id == vendor_id).first()
        if not vendor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found"
            )
        
        # Get user to get Firebase UID
        user = await AuthService.get_user_by_id(db, vendor_profile.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update status and reject reason in database
        vendor_profile.status = status_update.status
        if status_update.status == VendorStatus.REJECTED and status_update.reject_reason:
            vendor_profile.reject_reason = status_update.reject_reason
        elif status_update.status != VendorStatus.REJECTED:
            # Clear reject reason if status is not REJECTED
            vendor_profile.reject_reason = None
        db.commit()
        
        # Update Firebase custom claims
        firebase_success, firebase_message = await FirebaseService.set_vendor_status(
            user.firebase_uid, 
            status_update.status.value
        )
        
        if not firebase_success:
            logger.warning(f"Failed to update Firebase claims: {firebase_message}")
        
        logger.info(f"Vendor {vendor_id} status updated to {status_update.status.value}")
        
        return {
            "success": True,
            "message": f"Vendor status updated to {status_update.status.value}",
            "vendor_id": vendor_id,
            "new_status": status_update.status.value,
            "firebase_updated": firebase_success
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating vendor status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update vendor status"
        )

@router.post("/vendors/{vendor_id}/approve")
async def approve_vendor(
    vendor_id: int,
    db: Session = Depends(get_db),
    user_data: tuple = Depends(require_vendor_management)
):
    """
    Approve vendor (shortcut for updating status to APPROVED)
    """
    status_update = VendorStatusUpdate(status=VendorStatus.APPROVED)
    return await update_vendor_status(vendor_id, status_update, db, user_data)

@router.post("/vendors/{vendor_id}/reject")
async def reject_vendor(
    vendor_id: int,
    reject_request: VendorRejectRequest,
    db: Session = Depends(get_db),
    user_data: tuple = Depends(require_vendor_management)
):
    """
    Reject vendor (shortcut for updating status to REJECTED)
    """
    status_update = VendorStatusUpdate(
        status=VendorStatus.REJECTED,
        reject_reason=reject_request.reject_reason
    )
    return await update_vendor_status(vendor_id, status_update, db, user_data) 
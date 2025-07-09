from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db

from app.schemas.vendor import VendorProfileResponse, VendorProfileUpdateRequest, ApplyVendorRequest, ApplyVendorResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.middleware.firebase_auth import (
    require_vendor_role, 
    require_approved_vendor,
    get_current_user_with_role
)
from app.models.vendor_profile import VendorProfile, VendorStatus
import logging
from typing import List

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vendor", tags=["Vendor"])

@router.get("/profile", response_model=VendorProfileResponse)
async def get_vendor_profile(
    db: Session = Depends(get_db),
    user_data: tuple = Depends(require_vendor_role)
) -> VendorProfileResponse:
    """
    Get vendor profile (requires VENDOR role)
    """
    firebase_uid, custom_claims = user_data
    
    try:
        # Get user from database
        user = await AuthService.get_user_by_firebase_uid(db, firebase_uid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get vendor profile
        vendor_profile = db.query(VendorProfile).filter(VendorProfile.user_id == user.id).first()
        if not vendor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor profile not found"
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
            status=vendor_profile.status,
            created_at=vendor_profile.created_at.isoformat(),
            description=vendor_profile.description,
            reject_reason=vendor_profile.reject_reason
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting vendor profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get vendor profile"
        )

@router.put("/profile", response_model=VendorProfileResponse)
async def update_vendor_profile(
    profile_update: VendorProfileUpdateRequest,
    db: Session = Depends(get_db),
    user_data: tuple = Depends(require_vendor_role)
) -> VendorProfileResponse:
    """
    Update vendor profile business information (requires VENDOR role)
    """
    firebase_uid, custom_claims = user_data
    
    try:
        # Get user from database
        user = await AuthService.get_user_by_firebase_uid(db, firebase_uid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get vendor profile
        vendor_profile = db.query(VendorProfile).filter(VendorProfile.user_id == user.id).first()
        if not vendor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor profile not found"
            )
        
        # Update only provided fields
        update_data = profile_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(vendor_profile, field, value)
        
        db.commit()
        db.refresh(vendor_profile)
        
        logger.info(f"Vendor profile {vendor_profile.id} updated successfully")
        
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
            status=vendor_profile.status,
            created_at=vendor_profile.created_at.isoformat(),
            description=vendor_profile.description,
            reject_reason=vendor_profile.reject_reason
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating vendor profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update vendor profile"
        )

@router.get("/status")
async def get_vendor_status(
    user_data: tuple = Depends(require_vendor_role)
):
    """
    Get vendor status from token claims (requires VENDOR role)
    """
    firebase_uid, custom_claims = user_data
    
    return {
        "firebase_uid": firebase_uid,
        "user_type": custom_claims.get("user_type"),
        "vendor_status": custom_claims.get("vendor_status"),
        "is_approved": custom_claims.get("vendor_status") == "APPROVED"
    }

@router.get("/dashboard")
async def get_vendor_dashboard(
    user_data: tuple = Depends(require_approved_vendor)
):
    """
    Get vendor dashboard data (requires APPROVED vendor status)
    """
    firebase_uid, custom_claims = user_data
    
    # TODO: Implement actual dashboard data
    return {
        "message": "Welcome to vendor dashboard!",
        "firebase_uid": firebase_uid,
        "vendor_status": custom_claims.get("vendor_status"),
        "features": [
            "Product management",
            "Order management", 
            "Analytics",
            "Settings"
        ]
    }

@router.get("/products")
async def get_vendor_products(
    db: Session = Depends(get_db),
    user_data: tuple = Depends(require_vendor_role)
):
    """
    Get vendor's products (requires VENDOR role)
    """
    firebase_uid, custom_claims = user_data
    
    try:
        # Get user from database
        user = await AuthService.get_user_by_firebase_uid(db, firebase_uid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get vendor profile
        vendor_profile = db.query(VendorProfile).filter(VendorProfile.user_id == user.id).first()
        if not vendor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor profile not found"
            )
        
        # Get products (using dynamic relationship)
        products = vendor_profile.products.all()
        
        return {
            "products": [
                {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "status": product.status,
                    "quantity": product.quantity,
                    "created_at": product.created_at.isoformat()
                }
                for product in products
            ],
            "total_products": len(products)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting vendor products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get vendor products"
        )

@router.post("/reapply", response_model=ApplyVendorResponse)
async def reapply_vendor(
    request: ApplyVendorRequest,
    db: Session = Depends(get_db),
    user_data: tuple = Depends(require_vendor_role)
):
    """
    Reapply for vendor status (requires VENDOR role)
    """
    firebase_uid, custom_claims = user_data
    
    try:
        # Get user from database
        user = await AuthService.get_user_by_firebase_uid(db, firebase_uid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get vendor profile
        vendor_profile = db.query(VendorProfile).filter(VendorProfile.user_id == user.id).first()
        if not vendor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor profile not found"
            )
        
        # Check if vendor is in REJECTED status
        if vendor_profile.status != VendorStatus.REJECTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot reapply. Current status: {vendor_profile.status}"
            )
        
        # Update vendor profile with new data
        vendor_profile.business_type = request.business_type
        vendor_profile.business_name = request.business_name
        vendor_profile.organization_name = request.organization_name
        vendor_profile.legal_form = request.legal_form
        vendor_profile.inn = request.inn
        vendor_profile.registration_country = request.registration_country
        vendor_profile.registration_date = request.registration_date
        vendor_profile.passport_front_url = request.passport_front_url
        vendor_profile.passport_back_url = request.passport_back_url
        vendor_profile.status = VendorStatus.PENDING
        
        db.commit()
        db.refresh(vendor_profile)
        
        # Update Firebase custom claims
        from app.services.firebase_service import FirebaseService
        await FirebaseService.update_user_claims(firebase_uid, {
            "user_type": "VENDOR",
            "vendor_status": vendor_profile.status.value
        })
        
        logger.info(f"Vendor reapplied successfully: {vendor_profile.id}")
        
        return ApplyVendorResponse(
            success=True,
            message="Vendor reapplication submitted successfully",
            vendor_profile_id=vendor_profile.id,
            status=vendor_profile.status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error reapplying for vendor status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reapply for vendor status"
        )

# Import VendorProfile model
from app.models.vendor_profile import VendorProfile 

# Public vendor endpoints (no authentication required)
@router.get("/public/{vendor_id}/")
async def get_public_vendor_profile(
    vendor_id: int,
    db: Session = Depends(get_db)
):
    """
    Get public vendor profile information (no authentication required)
    """
    try:
        # Get vendor profile
        vendor_profile = db.query(VendorProfile).filter(VendorProfile.id == vendor_id).first()
        if not vendor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor profile not found"
            )
        
        # Get user information
        user = vendor_profile.user
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Only return approved vendors
        if vendor_profile.status != VendorStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor profile not found"
            )
        
        # Return public vendor information
        return {
            "id": vendor_profile.id,
            "user_id": vendor_profile.user_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "company_name": vendor_profile.business_name or vendor_profile.organization_name,
            "description": vendor_profile.description,
            "business_type": vendor_profile.business_type.value,
            "status": vendor_profile.status.value,
            "created_at": vendor_profile.created_at.isoformat(),
            "is_verified": vendor_profile.status == VendorStatus.APPROVED,
            "profile_image": None  # TODO: Add profile image field to vendor profile
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting public vendor profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get vendor profile"
        )

@router.get("/public/{vendor_id}/products/")
async def get_public_vendor_products(
    vendor_id: int,
    db: Session = Depends(get_db),
    limit: int = 10,
    offset: int = 0
):
    """
    Get public vendor products (no authentication required)
    """
    try:
        # Get vendor profile
        vendor_profile = db.query(VendorProfile).filter(VendorProfile.id == vendor_id).first()
        if not vendor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor profile not found"
            )
        
        # Only return products for approved vendors
        if vendor_profile.status != VendorStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor profile not found"
            )
        
        # Get products (using dynamic relationship)
        products_query = vendor_profile.products.filter(
            # Only return active products
            # Add any additional filters as needed
        )
        
        # Apply pagination
        total = products_query.count()
        products = products_query.offset(offset).limit(limit).all()
        
        return {
            "products": [
                {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "price": product.price,
                    "quantity": product.quantity,
                    "status": product.status,
                    "main_image_url": product.main_image_url,
                    "created_at": product.created_at.isoformat()
                }
                for product in products
            ],
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting public vendor products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get vendor products"
        ) 
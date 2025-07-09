from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.middleware.firebase_auth import require_vendor_role
from app.schemas.product import (
    ProductCreateComplete, ProductUpdateComplete, ProductResponse, ProductResponseSpecific
)
from app.services.product_service import ProductService
from app.utils.firebase_uid import get_vendor_profile_id_from_firebase_uid

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProductResponseSpecific)
async def create_product_complete(
    product: ProductCreateComplete,
    db: Session = Depends(get_db),
    user_data: tuple = Depends(require_vendor_role)
):
    """Create a product with all its variations, characteristics, and images in one request"""
    firebase_uid, _ = user_data
    
    vendor_profile_id = await get_vendor_profile_id_from_firebase_uid(db, firebase_uid)
    if not vendor_profile_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor profile not found"
        )
    
    service = ProductService(db)
    return service.create_complete(product, str(vendor_profile_id))

@router.get("/{product_id}", response_model=ProductResponseSpecific)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    user_data: tuple = Depends(require_vendor_role)
):
    """Get a product with all its relationships"""
    firebase_uid, _ = user_data
    
    vendor_profile_id = await get_vendor_profile_id_from_firebase_uid(db, firebase_uid)
    if not vendor_profile_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor profile not found"
        )
    
    service = ProductService(db)
    product = service.get(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if str(product.vendor_profile_id) != str(vendor_profile_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this product"
        )
    
    return product

@router.get("/", response_model=List[ProductResponseSpecific])
async def get_my_products(
    status: Optional[str] = Query(None, description="Filter by status: draft, pending, approved, rejected"),
    db: Session = Depends(get_db),
    user_data: tuple = Depends(require_vendor_role)
):
    """Get all products for the authenticated vendor with optional status filter"""
    firebase_uid, _ = user_data
    
    vendor_profile_id = await get_vendor_profile_id_from_firebase_uid(db, firebase_uid)
    if not vendor_profile_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor profile not found"
        )
    
    service = ProductService(db)
    return service.get_by_vendor(vendor_profile_id, status=status)

@router.put("/{product_id}", response_model=ProductResponseSpecific)
async def update_product_complete(
    product_id: int,
    product: ProductUpdateComplete,
    db: Session = Depends(get_db),
    user_data: tuple = Depends(require_vendor_role)
):
    """Update a product with all its relationships in one request"""
    firebase_uid, _ = user_data
    
    vendor_profile_id = await get_vendor_profile_id_from_firebase_uid(db, firebase_uid)
    if not vendor_profile_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor profile not found"
        )
    
    service = ProductService(db)
    return service.update_complete(product_id, product, str(vendor_profile_id))

@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    user_data: tuple = Depends(require_vendor_role)
):
    """Delete a product"""
    firebase_uid, _ = user_data
    
    vendor_profile_id = await get_vendor_profile_id_from_firebase_uid(db, firebase_uid)
    if not vendor_profile_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor profile not found"
        )
    
    service = ProductService(db)
    return service.delete(product_id, str(vendor_profile_id))
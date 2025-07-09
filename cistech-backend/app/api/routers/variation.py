from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.middleware.firebase_auth import require_vendor_role
from app.schemas.product import VariationResponse
from app.services.product_service import ProductService
from app.utils.firebase_uid import get_vendor_profile_id_from_firebase_uid

router = APIRouter(
    prefix="/variations",
    tags=["variations"]
)

@router.get("/product/{product_id}", response_model=List[VariationResponse])
async def get_product_variations(
    product_id: int,
    db: Session = Depends(get_db),
    # user_data: tuple = Depends(require_vendor_role)
):
    """Get all variations for a specific product"""
    # firebase_uid, _ = user_data
    
    # # Получаем vendor_profile_id через Firebase UID
    # vendor_profile_id = await get_vendor_profile_id_from_firebase_uid(db, firebase_uid)
    # if not vendor_profile_id:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="Vendor profile not found"
    #     )
    
    # Проверяем, принадлежит ли продукт данному вендору
    product_service = ProductService(db)
    product = product_service.get(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # if str(product.vendor_profile_id) != str(vendor_profile_id):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Not authorized to access variations for this product"
    #     )
    
    return product.variations

# Note: Individual variation CRUD operations are now handled through the main product endpoint
# This keeps the API simpler and ensures data consistency
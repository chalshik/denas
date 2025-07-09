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
    prefix="/products/public",
    tags=["products public"]
)

# Public endpoints for browsing products
@router.get("/", response_model=List[ProductResponse])
async def get_all_products(
    limit: Optional[int] = Query(None, description="Limit number of products returned"),
    offset: Optional[int] = Query(None, description="Number of products to skip"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    vendor_id: Optional[int] = Query(None, description="Filter by vendor ID"),
    search: Optional[str] = Query(None, description="Search by product name"),
    db: Session = Depends(get_db)
):
    """Get all approved products (public endpoint)"""
    service = ProductService(db)
    
    if vendor_id:
        # Get products by vendor
        products = service.get_by_vendor(vendor_id)
        # Filter only approved products for public access
        approved_products = [p for p in products if p.status == 'approved']
        return approved_products
    else:
        # Get all products with optional category filter and search
        products = service.get_all(approved_only=True, category_id=category_id, limit=limit, offset=offset, search_query=search)
        return products

@router.get("/category/{category_id}", response_model=List[ProductResponse])
async def get_products_by_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Get all approved products in a category (public endpoint)"""
    service = ProductService(db)
    products = service.get_by_category(category_id)
    # Filter only approved products for public access
    approved_products = [p for p in products if p.status == 'approved']
    return approved_products

@router.get("/search", response_model=List[ProductResponse])
async def search_products(
    q: str = Query(..., description="Search query for product name"),
    limit: Optional[int] = Query(None, description="Limit number of products returned"),
    offset: Optional[int] = Query(None, description="Number of products to skip"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    db: Session = Depends(get_db)
):
    """Search approved products by name (public endpoint)"""
    service = ProductService(db)
    products = service.search_products(
        search_query=q,
        category_id=category_id,
        approved_only=True,
        limit=limit,
        offset=offset
    )
    return products

@router.get("/search/filter-options", response_model=List[ProductResponse])
async def search_products_by_filter_options_only(
    filter_option_ids: List[int] = Query(..., description="Filter option IDs to search by"),
    match_all: bool = Query(False, description="Whether to match ALL filter options (true) or ANY (false)"),
    db: Session = Depends(get_db)
):
    """Search approved products by filter options only (public endpoint)"""
    service = ProductService(db)
    products = service.search_by_filter_options_only(
        filter_option_ids=filter_option_ids,
        match_all=match_all,
        approved_only=True
    )
    return products

@router.get("/{product_id}", response_model=ProductResponseSpecific)
async def get_product_public(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get a product (public endpoint) - only approved products"""
    service = ProductService(db)
    product = service.get(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if product.status != 'approved':
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not available"
        )
    
    # Обработка изображений продукта (основные изображения)
    for image in product.description_images:
        if not hasattr(image, 'product_id') or image.product_id is None:
            image.product_id = product.id
    
    # Обработка изображений вариаций
    for variation in product.variations:
        for image in variation.images:
            if not hasattr(image, 'product_id') or image.variation_id is None:
                image.variation_id = variation.id
    
    return product
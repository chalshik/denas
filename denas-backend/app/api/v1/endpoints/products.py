from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.db.database import get_db
from app.models.product import AvailabilityType
from app.schemas.product import (
    ProductCreateRequest, ProductUpdate, ProductResponse, 
    ProductCatalog, ProductResponseSpecific
)
from app.api.dependencies import require_admin_access
from app.models.user import User
from app.services.products_service import ProductService

logger = logging.getLogger(__name__)

router = APIRouter()

# PUBLIC ENDPOINTS - Catalog and Browse

@router.get("/", response_model=List[ProductCatalog])
async def get_products_catalog(
    # Pagination
    skip: int = Query(0, ge=0, description="Number of products to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of products to return"),
    
    # Filtering
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    availability_type: Optional[AvailabilityType] = Query(None, description="Filter by availability type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    search: Optional[str] = Query(None, description="Search in name or description"),
    
    db: Session = Depends(get_db)
):
    """
    Get products for catalog/listing views (public endpoint)
    Returns lightweight ProductCatalog with minimal data optimized for browsing:
    - Basic product info (id, name, price, availability)
    - Category name only
    - Primary image only
    - Favorites count
    """
    try:
        service = ProductService(db)
        
        # Use catalog-optimized method
        products = service.get_products_catalog(
            skip=skip,
            limit=limit,
            category_id=category_id,
            availability_type=availability_type,
            is_active=is_active,
            min_price=min_price,
            max_price=max_price,
            search=search
        )
        
        return products
        
    except Exception as e:
        logger.error(f"Unexpected error in get_products_catalog: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{product_id}", response_model=ProductResponseSpecific)
async def get_product_detailed(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed product information for specific product views (public endpoint)
    Returns comprehensive ProductResponseSpecific with full data:
    - Complete product information including description, stock quantity
    - Full category object with all details
    - All product images
    - Favorites count
    """
    try:
        service = ProductService(db)
        
        # Use detailed-optimized method
        product = service.get_product_detailed(product_id)
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        return product
        
    except HTTPException:
        # Re-raise HTTP exceptions from service layer
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_product_detailed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/category/{category_id}/products", response_model=List[ProductCatalog])
async def get_products_by_category(
    category_id: int,
    skip: int = Query(0, ge=0, description="Number of products to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of products to return"),
    availability_type: Optional[AvailabilityType] = Query(None, description="Filter by availability type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    db: Session = Depends(get_db)
):
    """
    Get products in a specific category for catalog views (public endpoint)
    Returns lightweight ProductCatalog optimized for category browsing
    """
    try:
        service = ProductService(db)
        
        # Use catalog method with category filter
        products = service.get_products_catalog(
            skip=skip,
            limit=limit,
            category_id=category_id,
            availability_type=availability_type,
            is_active=is_active,
            min_price=min_price,
            max_price=max_price
        )
        
        return products
        
    except Exception as e:
        logger.error(f"Unexpected error in get_products_by_category: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/search/products", response_model=List[ProductCatalog])
async def search_products(
    q: str = Query(..., description="Search query for product name or description"),
    skip: int = Query(0, ge=0, description="Number of products to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of products to return"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    availability_type: Optional[AvailabilityType] = Query(None, description="Filter by availability type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    db: Session = Depends(get_db)
):
    """
    Search products with text query for catalog views (public endpoint)
    Returns lightweight ProductCatalog optimized for search results
    """
    try:
        service = ProductService(db)
        
        # Use catalog method with search
        products = service.get_products_catalog(
            skip=skip,
            limit=limit,
            category_id=category_id,
            availability_type=availability_type,
            is_active=is_active,
            min_price=min_price,
            max_price=max_price,
            search=q
        )
        
        return products
        
    except Exception as e:
        logger.error(f"Unexpected error in search_products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# ADMIN ENDPOINTS - Full CRUD operations

@router.post("/", response_model=ProductResponseSpecific, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreateRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_access)
):
    """
    Create a new product with images (admin only)
    Returns detailed ProductResponseSpecific
    """
    try:
        service = ProductService(db)
        
        # Service handles all validation (category exists, etc.)
        product = service.create_product_with_images(product_data)
        
        logger.info(f"Product created: {product.name} (ID: {product.id}) by admin {admin_user.id}")
        return product
        
    except HTTPException:
        # Service layer provides proper HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in create_product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{product_id}", response_model=ProductResponseSpecific)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_access)
):
    """
    Update a product (admin only)
    Returns detailed ProductResponseSpecific
    """
    try:
        service = ProductService(db)
        
        # Service handles validation (product exists, category exists, etc.)
        updated_product = service.update_product(product_id, product_data)
        
        logger.info(f"Product updated: {updated_product.name} (ID: {product_id}) by admin {admin_user.id}")
        return updated_product
        
    except HTTPException:
        # Service layer provides proper HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in update_product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_access)
):
    """
    Delete a product (admin only)
    """
    try:
        service = ProductService(db)
        
        # Service handles validation (product exists) and deletion
        service.delete_product(product_id)
        
        logger.info(f"Product deleted (ID: {product_id}) by admin {admin_user.id}")
        return {"success": True, "message": "Product deleted successfully"}
        
    except HTTPException:
        # Service layer provides proper HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in delete_product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/admin/stats")
async def get_product_statistics(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_access)
):
    """
    Get product statistics (admin only)
    """
    try:
        service = ProductService(db)
        stats = service.get_product_stats()
        
        logger.info(f"Product stats requested by admin {admin_user.id}")
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_product_statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# LEGACY ENDPOINT - Backward compatibility

@router.get("/legacy/all", response_model=List[ProductResponse])
async def get_all_products_legacy(
    skip: int = Query(0, ge=0, description="Number of products to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of products to return"),
    product_id: Optional[int] = Query(None, description="Get specific product by ID"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    availability_type: Optional[AvailabilityType] = Query(None, description="Filter by availability type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    search: Optional[str] = Query(None, description="Search in name or description"),
    db: Session = Depends(get_db)
):
    """
    Legacy endpoint for backward compatibility
    Use /products/ (catalog) or /products/{id} (detailed) instead
    """
    try:
        service = ProductService(db)
        
        # Use legacy method for backward compatibility
        products = service.get_products_with_filters(
            skip=skip,
            limit=limit,
            product_id=product_id,
            category_id=category_id,
            availability_type=availability_type,
            is_active=is_active,
            min_price=min_price,
            max_price=max_price,
            search=search
        )
        
        # Service layer handles all business logic including 404 for single product
        if product_id and not products:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        return products
        
    except HTTPException:
        # Re-raise HTTP exceptions from service layer
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_all_products_legacy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 
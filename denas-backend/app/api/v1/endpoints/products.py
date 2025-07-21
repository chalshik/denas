from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
import logging

from app.db.session import get_db
from app.services.products_service import ProductService
from app.schemas.product import (
    Product, ProductCreate, ProductUpdate, ProductCatalog, 
    ProductWithDetails, ProductListResponse, AvailabilityType, AdminProductListResponse
)
from app.api.dependencies import get_current_user, require_admin_access, get_current_user_optional
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()


# Public endpoints for product catalog
@router.get("/catalog", response_model=ProductListResponse)
async def get_products_catalog(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    min_price: Optional[Decimal] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[Decimal] = Query(None, ge=0, description="Maximum price filter"),
    availability_type: Optional[AvailabilityType] = Query(None, description="Filter by availability type"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in product name and description"),
    sort_by: str = Query("created_at", description="Sort by: name, price, created_at"),
    sort_order: str = Query("desc", description="Sort order: asc, desc"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get products catalog with filtering, searching, and pagination (public endpoint)
    """
    try:
        skip = (page - 1) * size
        
        products, total = await ProductService.get_products_catalog(
            db=db,
            skip=skip,
            limit=size,
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            availability_type=availability_type,
            is_active=is_active,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            current_user=current_user
        )
        
        return ProductListResponse(
            items=products,
            total=total,
            page=page,
            size=size,
            has_next=skip + size < total,
            has_previous=page > 1
        )
        
    except Exception as e:
        logger.error(f"Error fetching products catalog: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch products catalog"
        )


@router.get("/featured", response_model=List[ProductCatalog])
async def get_featured_products(
    limit: int = Query(10, ge=1, le=50, description="Number of featured products to return"),
    db: Session = Depends(get_db)
):
    """
    Get featured products - latest active products that are in stock (public endpoint)
    """
    try:
        products = await ProductService.get_featured_products(db=db, limit=limit)
        
        # Convert to catalog format
        catalog_products = []
        for product in products:
            primary_image = next(
                (img for img in product.images if img.image_type.value == "official"),
                product.images[0] if product.images else None
            )
            
            catalog_product = ProductCatalog(
                id=product.id,
                name=product.name,
                price=product.price,
                image_url=primary_image.image_url if primary_image else None,
                availability_type=product.availability_type,
                is_active=product.is_active,
                category_id=product.category_id
            )
            catalog_products.append(catalog_product)
        
        return catalog_products
        
    except Exception as e:
        logger.error(f"Error fetching featured products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch featured products"
        )



@router.get("/{product_id}", response_model=ProductWithDetails)
async def get_product_details(
    product_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get detailed product information (public endpoint)
    """
    try:
        product = await ProductService.get_product_with_details(db=db, product_id=product_id)
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # If user is not admin, only show active products
        if not current_user or current_user.role.value not in ["Admin", "Manager"]:
            if not product.is_active:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product not found"
                )
        
        return product
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product details for {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch product details"
        )


# Admin endpoints
@router.get("/", response_model=AdminProductListResponse)
async def get_all_products(
    skip: int = Query(0, ge=0, description="Number of products to skip"),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of products to return"),
    include_inactive: bool = Query(False, description="Include inactive products"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    admin_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """
    Get all products with full details for admin management (admin only)
    Returns complete product information including category, images, and all fields
    By default shows only active products, set include_inactive=true to see all
    Supports filtering by category_id, min_price, and max_price
    """
    try:
        from sqlalchemy.orm import joinedload
        from app.models.product import Product
        
        # Build base query with all related data for full product details
        base_query = db.query(Product).options(
            joinedload(Product.images),    # Load all product images
            joinedload(Product.category)   # Load full category object
        )
        
        # Apply filters to base query
        if not include_inactive:
            base_query = base_query.filter(Product.is_active == True)
            
        if category_id is not None:
            base_query = base_query.filter(Product.category_id == category_id)
            
        if min_price is not None:
            base_query = base_query.filter(Product.price >= min_price)
            
        if max_price is not None:
            base_query = base_query.filter(Product.price <= max_price)
        
        # Get total count before applying pagination
        total = base_query.count()
        
        # Apply pagination
        products = base_query.offset(skip).limit(limit).all()
        
        # Calculate pagination info
        page = (skip // limit) + 1
        has_next = skip + limit < total
        has_previous = skip > 0
        
        return AdminProductListResponse(
            items=products,
            total=total,
            page=page,
            size=limit,
            has_next=has_next,
            has_previous=has_previous
        )
        
    except Exception as e:
        logger.error(f"Error fetching all products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch products"
        )


@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    admin_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """
    Create a new product (admin only)
    """
    try:
        product = await ProductService.create_product(db=db, product_data=product_data)
        
        logger.info(f"Product created successfully: {product.name} by admin {admin_user.id}")
        return product
        
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create product"
        )


@router.put("/{product_id}", response_model=Product)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    admin_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """
    Update a product (admin only)
    """
    try:
        product = await ProductService.update_product(
            db=db,
            product_id=product_id,
            product_data=product_data
        )
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        logger.info(f"Product updated successfully: {product.name} by admin {admin_user.id}")
        return product
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update product"
        )


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    admin_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """
    Delete a product (admin only)
    """
    try:
        deleted = await ProductService.delete_product(db=db, product_id=product_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        logger.info(f"Product deleted successfully by admin {admin_user.id}")
        return {"success": True, "message": "Product deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete product"
        )

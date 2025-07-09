from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import logging

from app.db.database import get_db
from app.models.product import Product as ProductModel, AvailabilityType
from app.models.category import Category as CategoryModel
from app.schemas.product import Product, ProductCreate, ProductUpdate, ProductWithDetails, ProductWithCategory
from app.api.dependencies import get_current_user_optional, require_admin_access
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()

# Public endpoints
@router.get("/", response_model=List[ProductWithCategory])
async def get_all_products(
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
    Get all products with filtering and pagination (public endpoint)
    """
    try:
        query = db.query(ProductModel).options(joinedload(ProductModel.category))
        
        # Apply filters
        if category_id:
            query = query.filter(ProductModel.category_id == category_id)
        if availability_type:
            query = query.filter(ProductModel.availability_type == availability_type)
        if is_active is not None:
            query = query.filter(ProductModel.is_active == is_active)
        if min_price is not None:
            query = query.filter(ProductModel.price >= min_price)
        if max_price is not None:
            query = query.filter(ProductModel.price <= max_price)
        
        products = query.offset(skip).limit(limit).all()
        return products
        
    except Exception as e:
        logger.error(f"Error fetching products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch products"
        )


@router.get("/{product_id}", response_model=ProductWithDetails)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific product by ID with full details (public endpoint)
    """
    try:
        product = db.query(ProductModel).options(
            joinedload(ProductModel.category),
            joinedload(ProductModel.images),
            joinedload(ProductModel.favorites)
        ).filter(ProductModel.id == product_id).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        return product
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch product"
        )


@router.get("/search/{search_term}", response_model=List[ProductWithCategory])
async def search_products(
    search_term: str,
    skip: int = Query(0, ge=0, description="Number of products to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of products to return"),
    db: Session = Depends(get_db)
):
    """
    Search products by name or description (public endpoint)
    """
    try:
        search_pattern = f"%{search_term}%"
        products = db.query(ProductModel).options(joinedload(ProductModel.category)).filter(
            (ProductModel.name.ilike(search_pattern)) |
            (ProductModel.description.ilike(search_pattern))
        ).offset(skip).limit(limit).all()
        
        return products
        
    except Exception as e:
        logger.error(f"Error searching products with term '{search_term}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search products"
        )


@router.get("/category/{category_id}/products", response_model=List[Product])
async def get_products_by_category(
    category_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all products in a specific category (public endpoint)
    """
    try:
        # Check if category exists
        category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        products = db.query(ProductModel).filter(
            ProductModel.category_id == category_id
        ).offset(skip).limit(limit).all()
        
        return products
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching products for category {category_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch products for category"
        )


# Admin endpoints
@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_access)
):
    """
    Create a new product (admin only)
    """
    try:
        # Check if category exists
        category = db.query(CategoryModel).filter(CategoryModel.id == product_data.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found"
            )
        
        # Create new product
        product = ProductModel(**product_data.dict())
        db.add(product)
        db.commit()
        db.refresh(product)
        
        logger.info(f"Product created successfully: {product.name} (ID: {product.id}) by admin {admin_user.id}")
        return product
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create product"
        )


@router.put("/{product_id}", response_model=Product)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_access)
):
    """
    Update a product (admin only)
    """
    try:
        # Get existing product
        product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Check if category exists (if category_id is being updated)
        if product_data.category_id and product_data.category_id != product.category_id:
            category = db.query(CategoryModel).filter(CategoryModel.id == product_data.category_id).first()
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category not found"
                )
        
        # Update product
        update_data = product_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        
        db.commit()
        db.refresh(product)
        
        logger.info(f"Product updated successfully: {product.name} (ID: {product.id}) by admin {admin_user.id}")
        return product
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update product"
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
        # Get product
        product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        product_name = product.name
        
        # Delete product
        db.delete(product)
        db.commit()
        
        logger.info(f"Product deleted successfully: {product_name} (ID: {product_id}) by admin {admin_user.id}")
        return {"success": True, "message": "Product deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete product"
        ) 
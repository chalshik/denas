from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import logging

from app.db.database import get_db
from app.schemas.product_image import ProductImage, ImageType
from app.models.product_image import ProductImage as ProductImageModel
from app.models.product import Product as ProductModel

logger = logging.getLogger(__name__)

router = APIRouter()

# Public read-only endpoints (images are now managed via ProductService)

@router.get("/", response_model=List[ProductImage])
async def get_product_images(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    image_type: Optional[ImageType] = Query(None, description="Filter by image type"),
    db: Session = Depends(get_db)
):
    """
    Get all product images with optional filters (public endpoint)
    """
    try:
        query = db.query(ProductImageModel)
        
        if product_id:
            query = query.filter(ProductImageModel.product_id == product_id)
        
        if image_type:
            query = query.filter(ProductImageModel.image_type == image_type)
        
        images = query.order_by(ProductImageModel.created_at.desc()).offset(skip).limit(limit).all()
        return images
        
    except Exception as e:
        logger.error(f"Error fetching product images: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch product images"
        )


@router.get("/{image_id}", response_model=ProductImage)
async def get_product_image(
    image_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific product image by ID (public endpoint)
    Note: Use product endpoints to get images with full product details
    """
    try:
        image = db.query(ProductImageModel).filter(ProductImageModel.id == image_id).first()
        
        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product image not found"
            )
        
        return image
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product image {image_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch product image"
        )


@router.get("/product/{product_id}/images", response_model=List[ProductImage])
async def get_images_by_product(
    product_id: int,
    image_type: Optional[ImageType] = Query(None, description="Filter by image type"),
    db: Session = Depends(get_db)
):
    """
    Get all images for a specific product (public endpoint)
    Note: To add/remove images, use the product endpoints
    """
    try:
        # Check if product exists
        product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        query = db.query(ProductImageModel).filter(ProductImageModel.product_id == product_id)
        
        if image_type:
            query = query.filter(ProductImageModel.image_type == image_type)
        
        images = query.order_by(ProductImageModel.created_at.desc()).all()
        return images
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching images for product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch product images"
        ) 
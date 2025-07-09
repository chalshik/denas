from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import logging

from app.db.database import get_db
from app.models.product_image import ProductImage as ProductImageModel, ImageType
from app.models.product import Product as ProductModel
from app.schemas.product_image import ProductImage, ProductImageCreate, ProductImageUpdate, ProductImageWithProduct
from app.api.dependencies import get_current_user_optional, require_admin_access
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()

# Public endpoints
@router.get("/", response_model=List[ProductImage])
async def get_all_product_images(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    image_type: Optional[ImageType] = Query(None, description="Filter by image type"),
    db: Session = Depends(get_db)
):
    """
    Get all product images with filtering (public endpoint)
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


@router.get("/{image_id}", response_model=ProductImageWithProduct)
async def get_product_image(
    image_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific product image by ID with product details (public endpoint)
    """
    try:
        image = db.query(ProductImageModel).options(
            joinedload(ProductImageModel.product)
        ).filter(ProductImageModel.id == image_id).first()
        
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


# Admin endpoints
@router.post("/", response_model=ProductImage, status_code=status.HTTP_201_CREATED)
async def create_product_image(
    image_data: ProductImageCreate,
    admin_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """
    Create a new product image (admin only)
    """
    try:
        # Check if product exists
        product = db.query(ProductModel).filter(ProductModel.id == image_data.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Create new product image
        product_image = ProductImageModel(**image_data.dict())
        db.add(product_image)
        db.commit()
        db.refresh(product_image)
        
        logger.info(f"Product image created successfully: ID {product_image.id} for product {product.id} by admin {admin_user.id}")
        return product_image
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating product image: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create product image"
        )


@router.put("/{image_id}", response_model=ProductImage)
async def update_product_image(
    image_id: int,
    image_data: ProductImageUpdate,
    admin_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """
    Update a product image (admin only)
    """
    try:
        # Get existing image
        image = db.query(ProductImageModel).filter(ProductImageModel.id == image_id).first()
        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product image not found"
            )
        
        # Check if product exists (if product_id is being updated)
        if image_data.product_id and image_data.product_id != image.product_id:
            product = db.query(ProductModel).filter(ProductModel.id == image_data.product_id).first()
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product not found"
                )
        
        # Update image
        update_data = image_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(image, field, value)
        
        db.commit()
        db.refresh(image)
        
        logger.info(f"Product image updated successfully: ID {image.id} by admin {admin_user.id}")
        return image
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating product image {image_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update product image"
        )


@router.delete("/{image_id}")
async def delete_product_image(
    image_id: int,
    admin_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """
    Delete a product image (admin only)
    """
    try:
        # Get image
        image = db.query(ProductImageModel).filter(ProductImageModel.id == image_id).first()
        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product image not found"
            )
        
        image_url = image.image_url
        product_id = image.product_id
        
        # Delete image
        db.delete(image)
        db.commit()
        
        logger.info(f"Product image deleted successfully: {image_url} (ID: {image_id}) for product {product_id} by admin {admin_user.id}")
        return {"success": True, "message": "Product image deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting product image {image_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete product image"
        )


@router.post("/bulk", response_model=List[ProductImage], status_code=status.HTTP_201_CREATED)
async def create_multiple_product_images(
    images_data: List[ProductImageCreate],
    admin_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """
    Create multiple product images in one request (admin only)
    """
    try:
        # Validate all products exist
        product_ids = list(set(image.product_id for image in images_data))
        existing_products = db.query(ProductModel.id).filter(ProductModel.id.in_(product_ids)).all()
        existing_product_ids = {p.id for p in existing_products}
        
        missing_products = set(product_ids) - existing_product_ids
        if missing_products:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Products not found: {list(missing_products)}"
            )
        
        # Create all images
        created_images = []
        for image_data in images_data:
            product_image = ProductImageModel(**image_data.dict())
            db.add(product_image)
            created_images.append(product_image)
        
        db.commit()
        
        # Refresh all images
        for image in created_images:
            db.refresh(image)
        
        logger.info(f"Bulk created {len(created_images)} product images by admin {admin_user.id}")
        return created_images
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating multiple product images: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create product images"
        )


@router.delete("/product/{product_id}/images")
async def delete_all_product_images(
    product_id: int,
    image_type: Optional[ImageType] = Query(None, description="Only delete images of this type"),
    admin_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """
    Delete all images for a specific product (admin only)
    """
    try:
        # Check if product exists
        product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Build query
        query = db.query(ProductImageModel).filter(ProductImageModel.product_id == product_id)
        
        if image_type:
            query = query.filter(ProductImageModel.image_type == image_type)
        
        # Count and delete
        images_count = query.count()
        query.delete()
        db.commit()
        
        type_msg = f" of type {image_type.value}" if image_type else ""
        logger.info(f"Deleted {images_count} product images{type_msg} for product {product_id} by admin {admin_user.id}")
        
        return {
            "success": True, 
            "message": f"Deleted {images_count} product images{type_msg}",
            "deleted_count": images_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting product images for product {product_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete product images"
        ) 
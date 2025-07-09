from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
import logging

from app.db.database import get_db
from app.models.category import Category as CategoryModel
from app.schemas.category import Category, CategoryCreate, CategoryUpdate, CategoryWithProducts
from app.api.dependencies import require_admin_access
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()

# Public endpoints (no authentication required)
@router.get("/", response_model=List[Category])
async def get_all_categories(
    skip: int = Query(0, ge=0, description="Number of categories to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of categories to return"),
    db: Session = Depends(get_db)
):
    """
    Get all categories (public endpoint)
    """
    try:
        categories = db.query(CategoryModel).offset(skip).limit(limit).all()
        return categories
        
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch categories"
        )


@router.get("/{category_id}", response_model=Category)
async def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific category by ID (public endpoint)
    """
    try:
        category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        return category
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching category {category_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch category"
        )


@router.get("/{category_id}/with-products", response_model=CategoryWithProducts)
async def get_category_with_products(
    category_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a category with all its products (public endpoint)
    """
    try:
        category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        return category
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching category {category_id} with products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch category with products"
        )


@router.get("/search/{search_term}", response_model=List[Category])
async def search_categories(
    search_term: str,
    skip: int = Query(0, ge=0, description="Number of categories to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of categories to return"),
    db: Session = Depends(get_db)
):
    """
    Search categories by name (public endpoint)
    """
    try:
        categories = db.query(CategoryModel).filter(
            CategoryModel.name.ilike(f"%{search_term}%")
        ).offset(skip).limit(limit).all()
        
        return categories
        
    except Exception as e:
        logger.error(f"Error searching categories with term '{search_term}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search categories"
        )


# Admin endpoints
@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_access)
):
    """
    Create a new category (admin only)
    """
    try:
        # Check if category with this name already exists
        existing_category = db.query(CategoryModel).filter(
            CategoryModel.name == category_data.name
        ).first()
        
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists"
            )
        
        # Create new category
        category = CategoryModel(**category_data.dict())
        db.add(category)
        db.commit()
        db.refresh(category)
        
        logger.info(f"Category created successfully: {category.name} by admin {admin_user.id}")
        return category
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating category: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create category"
        )


@router.put("/{category_id}", response_model=Category)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_access)
):
    """
    Update a category (admin only)
    """
    try:
        # Get existing category
        category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        # Check if new name already exists (if name is being updated)
        if category_data.name and category_data.name != category.name:
            existing_category = db.query(CategoryModel).filter(
                CategoryModel.name == category_data.name,
                CategoryModel.id != category_id
            ).first()
            
            if existing_category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category with this name already exists"
                )
        
        # Update category
        update_data = category_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)
        
        db.commit()
        db.refresh(category)
        
        logger.info(f"Category updated successfully: {category.name} by admin {admin_user.id}")
        return category
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating category {category_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update category"
        )


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_access)
):
    """
    Delete a category (admin only)
    """
    try:
        # Get category
        category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        # Delete category
        db.delete(category)
        db.commit()
        
        logger.info(f"Category deleted successfully: {category.name} by admin {admin_user.id}")
        return {"success": True, "message": "Category deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting category {category_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete category"
        ) 
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
import logging

from app.db.session import get_db
from app.services.category_service import CategoryService
from app.schemas.category import Category, CategoryCreate, CategoryUpdate, CategoryWithProducts, CategoryWithMetadata
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
        categories = await CategoryService.get_all_categories(db=db, skip=skip, limit=limit)
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
        category = await CategoryService.get_category_by_id(db=db, category_id=category_id)
        
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
        category = await CategoryService.get_category_with_products(db=db, category_id=category_id)
        
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
        categories = await CategoryService.search_categories(
            db=db,
            search_term=search_term,
            skip=skip,
            limit=limit
        )
        
        return categories
        
    except Exception as e:
        logger.error(f"Error searching categories with term '{search_term}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search categories"
        )


# Admin endpoints
@router.get("/admin/with-metadata", response_model=List[CategoryWithMetadata])
async def get_categories_with_metadata(
    skip: int = Query(0, ge=0, description="Number of categories to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of categories to return"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_access)
):
    """
    Get all categories with metadata (including delete permissions) for admin
    """
    try:
        categories = await CategoryService.get_all_categories_with_metadata(db=db, skip=skip, limit=limit)
        return categories
        
    except Exception as e:
        logger.error(f"Error fetching categories with metadata: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch categories with metadata"
        )


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
        category = await CategoryService.create_category(db=db, category_data=category_data)
        
        logger.info(f"Category created successfully: {category.name} by admin {admin_user.id}")
        return category
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating category: {str(e)}")
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
        category = await CategoryService.update_category(
            db=db,
            category_id=category_id,
            category_data=category_data
        )
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        logger.info(f"Category updated successfully: {category.name} by admin {admin_user.id}")
        return category
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating category {category_id}: {str(e)}")
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
    Note: Categories with associated products cannot be deleted
    """
    try:
        deleted = await CategoryService.delete_category(db=db, category_id=category_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        logger.info(f"Category deleted successfully by admin {admin_user.id}")
        return {"success": True, "message": "Category deleted successfully"}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting category {category_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete category"
        ) 
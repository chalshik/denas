from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, and_, desc, asc
from typing import Optional, List, Tuple
from decimal import Decimal
import logging

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate

logger = logging.getLogger(__name__)


class CategoryService:
    """Service for handling category operations"""
    
    @staticmethod
    async def get_all_categories(
        db: Session, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Category]:
        """Get all categories with pagination"""
        return db.query(Category).offset(skip).limit(limit).all()
    
    @staticmethod
    async def get_category_by_id(db: Session, category_id: int) -> Optional[Category]:
        """Get category by ID"""
        return db.query(Category).filter(Category.id == category_id).first()
    
    @staticmethod
    async def get_category_by_name(db: Session, name: str) -> Optional[Category]:
        """Get category by name"""
        return db.query(Category).filter(Category.name == name).first()
    
    @staticmethod
    async def search_categories(
        db: Session,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Category]:
        """Search categories by name"""
        return db.query(Category).filter(
            Category.name.ilike(f"%{search_term}%")
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    async def create_category(
        db: Session,
        category_data: CategoryCreate
    ) -> Category:
        """
        Create a new category
        Returns: created category
        Raises: IntegrityError if category with same name exists
        """
        try:
            # Check if category with this name already exists
            existing_category = await CategoryService.get_category_by_name(
                db, category_data.name
            )
            if existing_category:
                raise ValueError("Category with this name already exists")
            
            category = Category(**category_data.dict())
            db.add(category)
            db.commit()
            db.refresh(category)
            
            logger.info(f"Category created successfully: {category.name}")
            return category
            
        except ValueError:
            raise
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database integrity error creating category: {str(e)}")
            raise ValueError("Category with this name already exists")
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating category: {str(e)}")
            raise e
    
    @staticmethod
    async def update_category(
        db: Session,
        category_id: int,
        category_data: CategoryUpdate
    ) -> Optional[Category]:
        """
        Update category
        Returns: updated category or None if not found
        Raises: ValueError if new name conflicts with existing category
        """
        try:
            category = await CategoryService.get_category_by_id(db, category_id)
            if not category:
                return None
            
            # Check if new name conflicts with existing category
            update_data = category_data.dict(exclude_unset=True)
            if 'name' in update_data and update_data['name'] != category.name:
                existing_category = db.query(Category).filter(
                    Category.name == update_data['name'],
                    Category.id != category_id
                ).first()
                
                if existing_category:
                    raise ValueError("Category with this name already exists")
            
            # Update category
            for field, value in update_data.items():
                setattr(category, field, value)
            
            db.commit()
            db.refresh(category)
            
            logger.info(f"Category updated successfully: {category.name}")
            return category
            
        except ValueError:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating category {category_id}: {str(e)}")
            raise e
    
    @staticmethod
    async def delete_category(
        db: Session,
        category_id: int
    ) -> bool:
        """
        Delete category
        Returns: True if deleted, False if not found
        """
        try:
            category = await CategoryService.get_category_by_id(db, category_id)
            if not category:
                return False
            
            db.delete(category)
            db.commit()
            
            logger.info(f"Category deleted successfully: {category.name}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting category {category_id}: {str(e)}")
            raise e
    
    @staticmethod
    async def get_category_with_products(
        db: Session,
        category_id: int
    ) -> Optional[Category]:
        """Get category with all its products"""
        return db.query(Category).filter(Category.id == category_id).first()

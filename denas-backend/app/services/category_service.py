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
    async def get_all_categories_with_metadata(
        db: Session, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[dict]:
        """Get all categories with metadata (including can_delete status and product count)"""
        try:
            from app.models.product import Product
            
            categories = db.query(Category).offset(skip).limit(limit).all()
            categories_with_metadata = []
            
            for category in categories:
                # Count products in this category
                product_count = db.query(Product).filter(Product.category_id == category.id).count()
                can_delete = product_count == 0
                
                category_dict = {
                    "id": category.id,
                    "name": category.name,
                    "created_at": category.created_at,
                    "can_delete": can_delete,
                    "product_count": product_count
                }
                categories_with_metadata.append(category_dict)
            
            return categories_with_metadata
            
        except Exception as e:
            logger.error(f"Error fetching categories with metadata: {str(e)}")
            raise e
    
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
            
            # Create category without specifying ID (let auto-increment handle it)
            category_dict = category_data.dict()
            # Ensure no ID is passed to avoid conflicts
            category_dict.pop('id', None)
            
            category = Category(**category_dict)
            db.add(category)
            db.commit()
            db.refresh(category)
            
            logger.info(f"Category created successfully: {category.name}")
            return category
            
        except ValueError:
            raise
        except IntegrityError as e:
            db.rollback()
            error_msg = str(e)
            logger.error(f"Database integrity error creating category: {error_msg}")
            
            # Handle specific sequence conflict
            if "duplicate key value violates unique constraint" in error_msg and "categories_pkey" in error_msg:
                logger.error("Auto-increment sequence may be out of sync. Consider running: SELECT setval('categories_id_seq', (SELECT COALESCE(MAX(id), 0) + 1 FROM categories));")
                raise ValueError("Database sequence error. Please contact administrator.")
            else:
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
    async def can_delete_category(
        db: Session,
        category_id: int
    ) -> bool:
        """
        Check if category can be safely deleted (has no products)
        Returns: True if category can be deleted, False if it has products
        """
        try:
            from app.models.product import Product
            
            # Count products in this category
            product_count = db.query(Product).filter(Product.category_id == category_id).count()
            return product_count == 0
            
        except Exception as e:
            logger.error(f"Error checking if category {category_id} can be deleted: {str(e)}")
            return False
    
    @staticmethod
    async def delete_category(
        db: Session,
        category_id: int,
        force: bool = False
    ) -> bool:
        """
        Delete category
        Returns: True if deleted, False if not found
        Raises: ValueError if category has products and force=False
        """
        try:
            category = await CategoryService.get_category_by_id(db, category_id)
            if not category:
                return False
            
            # Check if category has products (unless force delete)
            if not force:
                can_delete = await CategoryService.can_delete_category(db, category_id)
                if not can_delete:
                    from app.models.product import Product
                    product_count = db.query(Product).filter(Product.category_id == category_id).count()
                    raise ValueError(f"Cannot delete category '{category.name}' because it has {product_count} associated product(s). Please move or delete the products first.")
            
            db.delete(category)
            db.commit()
            
            logger.info(f"Category deleted successfully: {category.name}")
            return True
            
        except ValueError:
            raise
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

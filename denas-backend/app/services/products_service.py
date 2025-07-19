from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, and_, desc, asc, or_
from typing import Optional, List, Tuple
from decimal import Decimal
import logging

from app.models.product import Product, AvailabilityType
from app.models.product_image import ProductImage, ImageType
from app.models.category import Category
from app.schemas.product import ProductCreate, ProductUpdate, ProductCatalog
from app.schemas.product_image import ProductImageCreate

logger = logging.getLogger(__name__)


class ProductService:
    """Service for handling product operations"""
    
    @staticmethod
    async def get_products_catalog(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        category_id: Optional[int] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        availability_type: Optional[AvailabilityType] = None,
        is_active: Optional[bool] = True,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[ProductCatalog], int]:
        """
        Get products for catalog with filtering, searching, and pagination
        Returns: (products, total_count)
        """
        query = db.query(Product).options(
            joinedload(Product.images)
        )
        
        # Apply filters
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
            
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
            
        if availability_type is not None:
            query = query.filter(Product.availability_type == availability_type)
            
        if is_active is not None:
            query = query.filter(Product.is_active == is_active)
            
        if search:
            query = query.filter(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%")
                )
            )
        
        # Apply sorting
        if sort_order.lower() == "desc":
            sort_func = desc
        else:
            sort_func = asc
            
        if sort_by == "price":
            query = query.order_by(sort_func(Product.price))
        elif sort_by == "name":
            query = query.order_by(sort_func(Product.name))
        else:  # default to created_at
            query = query.order_by(sort_func(Product.created_at))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        products = query.offset(skip).limit(limit).all()
        
        # Convert to catalog format
        catalog_products = []
        for product in products:
            # Get primary image
            primary_image = next(
                (img for img in product.images if img.image_type == ImageType.OFFICIAL),
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
        
        return catalog_products, total
    
    @staticmethod
    async def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        return db.query(Product).filter(Product.id == product_id).first()
    
    @staticmethod
    async def get_product_with_details(
        db: Session, 
        product_id: int
    ) -> Optional[Product]:
        """Get product with all related data (category, images)"""
        return db.query(Product).options(
            joinedload(Product.category),
            joinedload(Product.images)
        ).filter(Product.id == product_id).first()
    
    @staticmethod
    async def create_product(
        db: Session,
        product_data: ProductCreate
    ) -> Product:
        """
        Create a new product with images
        Returns: created product
        """
        try:
            # Create product
            product_dict = product_data.dict(exclude={'image_urls'})
            product = Product(**product_dict)
            
            db.add(product)
            db.flush()  # Flush to get the ID
            
            # Create product images if provided
            if product_data.image_urls:
                for image_url in product_data.image_urls:
                    product_image = ProductImage(
                        product_id=product.id,
                        image_url=image_url,
                        image_type=ImageType.OFFICIAL
                    )
                    db.add(product_image)
            
            db.commit()
            db.refresh(product)
            
            logger.info(f"Product created successfully: {product.name}")
            return product
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database integrity error creating product: {str(e)}")
            raise e
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating product: {str(e)}")
            raise e
    
    @staticmethod
    async def update_product(
        db: Session,
        product_id: int,
        product_data: ProductUpdate
    ) -> Optional[Product]:
        """
        Update product
        Returns: updated product or None if not found
        """
        try:
            product = await ProductService.get_product_by_id(db, product_id)
            if not product:
                return None
            
            # Update product fields
            update_data = product_data.dict(exclude_unset=True, exclude={'image_urls'})
            for field, value in update_data.items():
                setattr(product, field, value)
            
            # Update images if provided
            if product_data.image_urls is not None:
                # Delete existing images
                db.query(ProductImage).filter(ProductImage.product_id == product_id).delete()
                
                # Create new images
                for image_url in product_data.image_urls:
                    product_image = ProductImage(
                        product_id=product.id,
                        image_url=image_url,
                        image_type=ImageType.OFFICIAL
                    )
                    db.add(product_image)
            
            db.commit()
            db.refresh(product)
            
            logger.info(f"Product updated successfully: {product.name}")
            return product
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating product {product_id}: {str(e)}")
            raise e
    
    @staticmethod
    async def delete_product(
        db: Session,
        product_id: int
    ) -> bool:
        """
        Delete product
        Returns: True if deleted, False if not found
        """
        try:
            product = await ProductService.get_product_by_id(db, product_id)
            if not product:
                return False
            
            db.delete(product)
            db.commit()
            
            logger.info(f"Product deleted successfully: {product.name}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting product {product_id}: {str(e)}")
            raise e
    
    @staticmethod
    async def search_products(
        db: Session,
        search_term: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[Product]:
        """Search products by name or description"""
        return db.query(Product).filter(
            or_(
                Product.name.ilike(f"%{search_term}%"),
                Product.description.ilike(f"%{search_term}%")
            )
        ).filter(Product.is_active == True).offset(skip).limit(limit).all()
    
    @staticmethod
    async def get_products_by_category(
        db: Session,
        category_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[Product]:
        """Get products by category"""
        return db.query(Product).filter(
            Product.category_id == category_id,
            Product.is_active == True
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    async def get_featured_products(
        db: Session,
        limit: int = 10
    ) -> List[Product]:
        """Get featured products (latest or most popular)"""
        return db.query(Product).filter(
            Product.is_active == True,
            Product.availability_type == "IN_STOCK"
        ).order_by(desc(Product.created_at)).limit(limit).all()

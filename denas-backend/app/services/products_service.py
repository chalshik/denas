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
from app.services.supabase_storage import get_supabase_storage

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
        sort_order: str = "desc",
        current_user: Optional[object] = None
    ) -> Tuple[List[ProductCatalog], int]:
        """
        Get products for catalog with filtering, searching, and pagination
        Catalog always returns only active products
        Returns: (products, total_count)
        """
        query = db.query(Product).options(
            joinedload(Product.images)
        )
        
        # Always filter for active products only in catalog
        query = query.filter(Product.is_active == True)
        
        # Apply filters
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
            
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
            
        if availability_type is not None:
            query = query.filter(Product.availability_type == availability_type)
            
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
        
        # Get user favorites for these products if user is authenticated
        user_favorites = set()
        if current_user:
            from app.models.favorite import Favorite
            product_ids = [product.id for product in products]
            favorites = db.query(Favorite).filter(
                Favorite.user_id == current_user.id,
                Favorite.product_id.in_(product_ids)
            ).all()
            user_favorites = {fav.product_id for fav in favorites}
        
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
                category_id=product.category_id,
                is_favorited=product.id in user_favorites if current_user else None
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
        Update product with proper image cleanup
        Returns: updated product or None if not found
        """
        try:
            product = await ProductService.get_product_by_id(db, product_id)
            if not product:
                return None

            # Get current images before updating
            current_images = db.query(ProductImage).filter(ProductImage.product_id == product_id).all()
            current_image_urls = [img.image_url for img in current_images]

            # Update product fields
            update_data = product_data.dict(exclude_unset=True, exclude={'image_urls'})
            for field, value in update_data.items():
                setattr(product, field, value)

            # Update images if provided
            if product_data.image_urls is not None:
                new_image_urls = product_data.image_urls
                
                # Determine which images to delete from storage
                images_to_delete = [url for url in current_image_urls if url not in new_image_urls]
                
                if images_to_delete:
                    # Clean up old images from Supabase storage
                    try:
                        storage = get_supabase_storage()
                        file_paths_to_delete = storage.extract_file_paths_from_urls(images_to_delete)
                        delete_result = storage.delete_files(file_paths_to_delete)
                        logger.info(f"Cleaned up {delete_result['deleted']} old images from storage for product {product_id}")
                        if delete_result['failed'] > 0:
                            logger.warning(f"Failed to delete {delete_result['failed']} images from storage")
                    except Exception as storage_error:
                        logger.error(f"Failed to clean up old images from storage: {str(storage_error)}")
                        # Continue with database update even if storage cleanup fails

                # Delete existing image records
                db.query(ProductImage).filter(ProductImage.product_id == product_id).delete()

                # Create new image records
                for image_url in new_image_urls:
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
        Delete product with proper image cleanup
        Returns: True if deleted, False if not found
        """
        try:
            product = await ProductService.get_product_by_id(db, product_id)
            if not product:
                return False

            # Get all images for this product before deletion
            product_images = db.query(ProductImage).filter(ProductImage.product_id == product_id).all()
            image_urls = [img.image_url for img in product_images]

            # Clean up images from Supabase storage
            if image_urls:
                try:
                    storage = get_supabase_storage()
                    file_paths_to_delete = storage.extract_file_paths_from_urls(image_urls)
                    delete_result = storage.delete_files(file_paths_to_delete)
                    logger.info(f"Cleaned up {delete_result['deleted']} images from storage for deleted product {product_id}")
                    if delete_result['failed'] > 0:
                        logger.warning(f"Failed to delete {delete_result['failed']} images from storage during product deletion")
                except Exception as storage_error:
                    logger.error(f"Failed to clean up images from storage during product deletion: {str(storage_error)}")
                    # Continue with product deletion even if storage cleanup fails

            # Delete the product (this will cascade delete images due to foreign key relationship)
            db.delete(product)
            db.commit()

            logger.info(f"Product deleted successfully: {product.name}")
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting product {product_id}: {str(e)}")
            raise e
    

    
    @staticmethod
    async def get_featured_products(
        db: Session,
        limit: int = 10
    ) -> List[Product]:
        """Get featured products (latest or most popular)"""
        return db.query(Product).filter(
            Product.is_active == True,
            Product.availability_type == AvailabilityType.IN_STOCK.value
        ).order_by(desc(Product.created_at)).limit(limit).all()

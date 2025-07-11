from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, or_, case, exists
from typing import List, Optional, Tuple, Dict, Any
from fastapi import HTTPException, status

from app.models.product import Product, AvailabilityType
from app.models.product_image import ProductImage
from app.models.favorite import Favorite
from app.models.category import Category
from app.schemas.product import ProductCreateRequest, ProductUpdate
from app.schemas.product_image import ProductImageCreate


class ProductQueryBuilder:
    """Separate query building logic for better testability and reusability"""
    
    def __init__(self, db: Session):
        self.db = db
        
    def base_query_with_relationships(self):
        """Build base query with optimized eager loading for detailed views"""
        return self.db.query(Product).options(
            joinedload(Product.category),
            selectinload(Product.images),  # Better for 1-to-many relationships
        )
    
    def base_query_catalog(self):
        """Build base query optimized for catalog views (lightweight)"""
        return self.db.query(Product).options(
            joinedload(Product.category),
            # Load only first image for catalog view - use limit in subquery
            selectinload(Product.images).options()
        )
    
    def add_favorites_count_subquery(self, query):
        """Add favorites count as a subquery to avoid N+1"""
        favorites_subquery = (
            self.db.query(func.count(Favorite.id))
            .filter(Favorite.product_id == Product.id)
            .correlate(Product)
            .scalar_subquery()
        )
        
        return query.add_columns(favorites_subquery.label('favorites_count'))
    
    def apply_filters(self, query, filters: Dict[str, Any]):
        """Apply filters in a centralized, testable way"""
        if filters.get('product_id'):
            query = query.filter(Product.id == filters['product_id'])
            
        if filters.get('category_id'):
            query = query.filter(Product.category_id == filters['category_id'])
            
        if filters.get('availability_type'):
            query = query.filter(Product.availability_type == filters['availability_type'])
            
        if filters.get('is_active') is not None:
            query = query.filter(Product.is_active == filters['is_active'])
            
        if filters.get('min_price') is not None:
            query = query.filter(Product.price >= filters['min_price'])
            
        if filters.get('max_price') is not None:
            query = query.filter(Product.price <= filters['max_price'])
            
        if filters.get('search'):
            search_pattern = f"%{filters['search']}%"
            query = query.filter(
                or_(
                    Product.name.ilike(search_pattern),
                    Product.description.ilike(search_pattern)
                )
            )
        
        return query
    
    def apply_pagination(self, query, skip: int = 0, limit: int = 50):
        """Apply pagination"""
        return query.offset(skip).limit(limit)


class ProductValidator:
    """Separate validation logic"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def validate_category_exists(self, category_id: int) -> None:
        """Validate category exists and is active"""
        category = self.db.query(Category).filter(
            Category.id == category_id,
            Category.is_active == True
        ).first()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with ID {category_id} not found or inactive"
            )
    
    def validate_product_exists(self, product_id: int) -> Product:
        """Validate product exists and return it"""
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return product


class ProductService:
    def __init__(self, db: Session):
        self.db = db
        self.query_builder = ProductQueryBuilder(db)
        self.validator = ProductValidator(db)

    def get_products_catalog(
        self,
        skip: int = 0,
        limit: int = 50,
        category_id: Optional[int] = None,
        availability_type: Optional[AvailabilityType] = None,
        is_active: Optional[bool] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        search: Optional[str] = None,
    ) -> List[Product]:
        """
        Get products for catalog/listing views with lightweight data.
        Optimized for browsing: minimal product info, category name, primary image only.
        """
        # Build filters dict
        filters = {
            'category_id': category_id,
            'availability_type': availability_type,
            'is_active': is_active,
            'min_price': min_price,
            'max_price': max_price,
            'search': search
        }
        
        # Build optimized catalog query
        query = self.query_builder.base_query_catalog()
        query = self.query_builder.add_favorites_count_subquery(query)
        query = self.query_builder.apply_filters(query, filters)
        query = self.query_builder.apply_pagination(query, skip, limit)
        
        # Execute query
        results = query.all()
        
        # Process results for catalog view
        products = []
        for result in results:
            if isinstance(result, tuple):
                product, favorites_count = result
                product.favorites_count = favorites_count or 0
            else:
                product = result
                product.favorites_count = 0
            
            # Add primary image for catalog view
            if product.images:
                product.primary_image = product.images[0]  # First image as primary
            else:
                product.primary_image = None
                
            products.append(product)
        
        return products

    def get_product_detailed(self, product_id: int) -> Optional[Product]:
        """
        Get a single product with full details for specific product views.
        Includes all images, full category info, description, stock, etc.
        """
        filters = {'product_id': product_id}
        
        # Build detailed query with full relationships
        query = self.query_builder.base_query_with_relationships()
        query = self.query_builder.add_favorites_count_subquery(query)
        query = self.query_builder.apply_filters(query, filters)
        query = self.query_builder.apply_pagination(query, 0, 1)
        
        # Execute query
        results = query.all()
        
        if not results:
            return None
        
        # Process result for detailed view
        result = results[0]
        if isinstance(result, tuple):
            product, favorites_count = result
            product.favorites_count = favorites_count or 0
        else:
            product = result
            product.favorites_count = 0
        
        return product

    def get_products_with_filters(
        self,
        skip: int = 0,
        limit: int = 50,
        product_id: Optional[int] = None,
        category_id: Optional[int] = None,
        availability_type: Optional[AvailabilityType] = None,
        is_active: Optional[bool] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        search: Optional[str] = None,
    ) -> List[Product]:
        """
        Get products with comprehensive filtering and optimized loading.
        Uses single query with subqueries to avoid N+1 problems.
        
        DEPRECATED: Use get_products_catalog() or get_product_detailed() instead.
        Kept for backward compatibility.
        """
        # Build filters dict
        filters = {
            'product_id': product_id,
            'category_id': category_id,
            'availability_type': availability_type,
            'is_active': is_active,
            'min_price': min_price,
            'max_price': max_price,
            'search': search
        }
        
        # Override limit for single product query
        if product_id:
            limit = 1
        
        # Build optimized query
        query = self.query_builder.base_query_with_relationships()
        query = self.query_builder.add_favorites_count_subquery(query)
        query = self.query_builder.apply_filters(query, filters)
        query = self.query_builder.apply_pagination(query, skip, limit)
        
        # Execute query
        results = query.all()
        
        # Process results - separate products and favorites counts
        products = []
        for result in results:
            if isinstance(result, tuple):
                product, favorites_count = result
                product.favorites_count = favorites_count or 0
            else:
                product = result
                product.favorites_count = 0
            products.append(product)
        
        return products

    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """
        Get a single product by ID with optimized loading.
        Returns None if not found (no exceptions).
        
        DEPRECATED: Use get_product_detailed() instead.
        Kept for backward compatibility.
        """
        products = self.get_products_with_filters(product_id=product_id, limit=1)
        return products[0] if products else None

    def create_product_with_images(self, product_data: ProductCreateRequest) -> Product:
        """
        Create a product with images in a single transaction.
        All validation and business logic separated.
        """
        # Validate category first (business logic)
        self.validator.validate_category_exists(product_data.category_id)
        
        try:
            # Extract images data
            images_data = product_data.images.copy() if product_data.images else []
            
            # Create product
            product_dict = product_data.dict(exclude={'images'})
            product = Product(**product_dict)
            
            self.db.add(product)
            self.db.flush()  # Get ID without committing
            
            # Create images if provided
            if images_data:
                self._create_product_images(product.id, images_data)
            
            self.db.commit()
            
            # Return product with full details using optimized query
            created_product = self.get_product_detailed(product.id)
            if not created_product:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to retrieve created product"
                )
            
            return created_product
            
        except HTTPException:
            self.db.rollback()
            raise
        except IntegrityError as e:
            self.db.rollback()
            # Convert database errors to business errors
            if "foreign key constraint" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid foreign key reference"
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data integrity error"
            )
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create product: {str(e)}"
            )

    def update_product(self, product_id: int, product_data: ProductUpdate) -> Product:
        """
        Update a product with proper validation and transaction handling.
        """
        # Validate product exists
        product = self.validator.validate_product_exists(product_id)
        
        # Validate category if being updated
        update_data = product_data.dict(exclude_unset=True)
        if 'category_id' in update_data and update_data['category_id'] != product.category_id:
            self.validator.validate_category_exists(update_data['category_id'])
        
        try:
            # Apply updates
            for field, value in update_data.items():
                setattr(product, field, value)
            
            self.db.commit()
            
            # Return updated product with full details
            updated_product = self.get_product_detailed(product_id)
            if not updated_product:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to retrieve updated product"
                )
            
            return updated_product
            
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update product: {str(e)}"
            )

    def delete_product(self, product_id: int) -> bool:
        """
        Delete a product with proper validation.
        Returns True if deleted, raises exception if not found.
        """
        # Validate product exists (will raise HTTPException if not found)
        product = self.validator.validate_product_exists(product_id)
        
        try:
            self.db.delete(product)
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete product: {str(e)}"
            )
    
    def get_product_stats(self) -> Dict[str, Any]:
        """
        Get product statistics with optimized queries.
        """
        try:
            # Single query to get all counts
            stats_query = self.db.query(
                func.count(Product.id).label('total_products'),
                func.count(case([(Product.is_active == True, Product.id)])).label('active_products'),
                func.count(case([(Product.is_active == False, Product.id)])).label('inactive_products'),
                func.avg(Product.price).label('average_price'),
                func.min(Product.price).label('min_price'),
                func.max(Product.price).label('max_price')
            ).first()
            
            # Get products by availability type
            availability_stats = self.db.query(
                Product.availability_type,
                func.count(Product.id).label('count')
            ).group_by(Product.availability_type).all()
            
            return {
                'total_products': stats_query.total_products or 0,
                'active_products': stats_query.active_products or 0,
                'inactive_products': stats_query.inactive_products or 0,
                'average_price': float(stats_query.average_price or 0),
                'min_price': float(stats_query.min_price or 0),
                'max_price': float(stats_query.max_price or 0),
                'by_availability': {
                    str(stat.availability_type.value): stat.count 
                    for stat in availability_stats
                }
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve product statistics: {str(e)}"
            )
    
    def _create_product_images(self, product_id: int, images_data: List[ProductImageCreate]) -> None:
        """
        Helper method to create product images.
        Separated for better testability.
        """
        for image_data in images_data:
            product_image = ProductImage(
                product_id=product_id,
                image_url=image_data.image_url,
                image_type=image_data.image_type
            )
            self.db.add(product_image)

import logging
from typing import Optional, List, Dict, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from fastapi import HTTPException

from app.models.product.product import Product, ProductVariation
from app.models.product.filter import FilterOption, product_filters
from app.models.product.image import ProductImage, VariationImage
from app.models.product.characteristic import CharacteristicType, VariationCharacteristic, ProductCharacteristic
from app.models.vendor_profile import VendorProfile
from app.schemas.product import (
    ProductCreateComplete, ProductUpdateComplete, ProductResponse, ProductResponseSpecific,
    CharacteristicInput, VariationInput, CategoryResponse, ProductVendorProfileResponse,
    UserResponse, ProductImageResponse, VariationImageResponse, FilterOptionResponse,
    CharacteristicResponse, VariationResponse
)
from app.models.product.category import Category
import datetime

logger = logging.getLogger(__name__)

class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def get_raw(self, product_id: int) -> Optional[Product]:
        """Get raw SQLAlchemy Product model for internal use"""
        product = (self.db.query(Product)
                   .options(
                       joinedload(Product.category),
                       joinedload(Product.characteristics).joinedload(ProductCharacteristic.type),
                       joinedload(Product.variations).joinedload(ProductVariation.characteristics).joinedload(VariationCharacteristic.type),
                       joinedload(Product.variations).joinedload(ProductVariation.images),
                       joinedload(Product.description_images),
                       joinedload(Product.filters)
                   )
                   .filter(Product.id == product_id)
                   .first())
        
        if product:
            # Добавляем type_name для характеристик продукта
            for char in product.characteristics:
                char.type_name = char.type.name if char.type else ""
            
            # Добавляем type_name для характеристик вариаций
            for variation in product.variations:
                for char in variation.characteristics:
                    char.type_name = char.type.name if char.type else ""
        
        return product

    def get(self, product_id: int) -> Optional[ProductResponseSpecific]:
        """Get product by ID and return as ProductResponseSpecific"""
        product = (self.db.query(Product)
                   .options(
                       joinedload(Product.category),
                       joinedload(Product.vendor_profile).joinedload(VendorProfile.user),
                       joinedload(Product.characteristics).joinedload(ProductCharacteristic.type),
                       joinedload(Product.variations).joinedload(ProductVariation.characteristics).joinedload(VariationCharacteristic.type),
                       joinedload(Product.variations).joinedload(ProductVariation.images),
                       joinedload(Product.description_images),
                       joinedload(Product.filters).joinedload(FilterOption.filter_type)
                   )
                   .filter(Product.id == product_id)
                   .first())
        
        if not product:
            return None
        
        return self._convert_to_response_specific(product)

    def get_by_vendor(self, vendor_profile_id: int, status: Optional[str] = None) -> List[ProductResponseSpecific]:
        query = (self.db.query(Product)
                .options(
                    joinedload(Product.category),
                    joinedload(Product.vendor_profile).joinedload(VendorProfile.user),
                    joinedload(Product.characteristics).joinedload(ProductCharacteristic.type),
                    joinedload(Product.variations).joinedload(ProductVariation.characteristics).joinedload(VariationCharacteristic.type),
                    joinedload(Product.variations).joinedload(ProductVariation.images),
                    joinedload(Product.description_images),
                    joinedload(Product.filters).joinedload(FilterOption.filter_type)
                )
                .filter(Product.vendor_profile_id == vendor_profile_id))
        
        # Filter by status if specified
        if status:
            query = query.filter(Product.status == status)
        
        products = query.all()
        
        # Convert to proper response models to avoid serialization issues
        return [self._convert_to_response_specific(product) for product in products]
    
    def get_by_category(self, category_id: int) -> List[Product]:
        return (self.db.query(Product)
                .options(
                    joinedload(Product.category),
                    joinedload(Product.characteristics).joinedload(ProductCharacteristic.type),
                    joinedload(Product.variations).joinedload(ProductVariation.characteristics).joinedload(VariationCharacteristic.type),
                    joinedload(Product.variations).joinedload(ProductVariation.images),
                    joinedload(Product.description_images),
                    joinedload(Product.filters)
                )
                .filter(Product.category_id == category_id)
                .all())

    def _get_or_create_characteristic_type(self, type_name: str) -> CharacteristicType:
        """Get existing characteristic type or create new one"""
        char_type = (self.db.query(CharacteristicType)
                    .filter(CharacteristicType.name == type_name)
                    .first())
        
        if not char_type:
            char_type = CharacteristicType(name=type_name)
            self.db.add(char_type)
            self.db.flush()
        
        return char_type

    def _create_variation_characteristics(self, variation_id: int, characteristics: List[CharacteristicInput]):
        """Create characteristics for a variation"""
        for char_input in characteristics:
            # Get or create characteristic type
            char_type = self._get_or_create_characteristic_type(char_input.type_name)
            
            # Create the characteristic
            characteristic = VariationCharacteristic(
                variation_id=variation_id,
                characteristic_type_id=char_type.id,
                value=char_input.value
            )
            self.db.add(characteristic)

    def _create_variation_images(self, variation_id: int, images: List):
        """Create images for a variation"""
        for idx, img_data in enumerate(images):
            image = VariationImage(
                variation_id=variation_id,
                url=img_data.url,
                alt_text=img_data.alt_text,
                order=img_data.order or idx
            )
            self.db.add(image)

    def _create_product_images(self, product_id: int, images: List):
        """Create images for a product"""
        for idx, img_data in enumerate(images):
            image = ProductImage(
                product_id=product_id,
                url=img_data.url,
                alt_text=img_data.alt_text,
                order=img_data.order or idx
            )
            self.db.add(image)

    def _create_variations(self, product_id: int, variations: List[VariationInput]):
        """Create all variations for a product"""
        for var_data in variations:
            # Create variation without relationships
            variation_dict = var_data.model_dump(exclude={"characteristics", "images"})
            variation_dict["product_id"] = product_id
            
            variation = ProductVariation(**variation_dict)
            self.db.add(variation)
            self.db.flush()  # Get ID
            
            # Add characteristics
            if var_data.characteristics:
                self._create_variation_characteristics(variation.id, var_data.characteristics)
            
            # Add images
            if var_data.images:
                self._create_variation_images(variation.id, var_data.images)

    def _create_product_characteristics(self, product_id: int, characteristics: List[CharacteristicInput]):
        """Create characteristics for a product"""
        for char_input in characteristics:
            # Get or create characteristic type
            char_type = self._get_or_create_characteristic_type(char_input.type_name)
            
            # Create the characteristic
            characteristic = ProductCharacteristic(
                product_id=product_id,
                characteristic_type_id=char_type.id,
                value=char_input.value
            )
            self.db.add(characteristic)

    def create_complete(self, payload: ProductCreateComplete, vendor_profile_id: str) -> ProductResponseSpecific:
        """Create a product with all its relationships in one transaction"""
        try:
            # Create the main product
            product_data = payload.model_dump(
                exclude={"filter_option_ids", "images", "characteristics", "variations"}
            )
            product_data["vendor_profile_id"] = vendor_profile_id
            
            product = Product(**product_data)
            self.db.add(product)
            self.db.flush()  # Get ID without committing
            
            # Add filter options if provided
            if payload.filter_option_ids:
                filter_options = (self.db.query(FilterOption)
                                 .filter(FilterOption.id.in_(payload.filter_option_ids))
                                 .all())
                if len(filter_options) != len(payload.filter_option_ids):
                    raise HTTPException(status_code=400, detail="Some filter options not found")
                product.filters = filter_options
            
            # Add product images
            if payload.images:
                self._create_product_images(product.id, payload.images)
            
            # Add product characteristics
            if payload.characteristics:
                self._create_product_characteristics(product.id, payload.characteristics)
            
            # Add variations
            if payload.variations:
                self._create_variations(product.id, payload.variations)
            
            self.db.commit()
            self.db.refresh(product)
            
            # Convert to proper Pydantic response model to avoid serialization issues
            return self._convert_to_response_specific(product)
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail=f"Failed to create product: {str(e)}")

    def update_complete(self, product_id: int, payload: ProductUpdateComplete, vendor_profile_id: str) -> ProductResponseSpecific:
        """Update a product completely"""
        product = self.get_raw(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
            
        if str(product.vendor_profile_id) != str(vendor_profile_id):
            raise HTTPException(status_code=403, detail="Not authorized to update this product")
        
        data = payload.model_dump(exclude={"filter_option_ids", "images", "characteristics", "variations"}, exclude_unset=True)
        for field, value in data.items():
            setattr(product, field, value)
        
        if payload.filter_option_ids is not None:
            current_filter_ids = set([f.id for f in product.filters]) if product.filters else set()
            new_filter_ids = set(payload.filter_option_ids)
            
            if current_filter_ids != new_filter_ids:
                if len(payload.filter_option_ids) == 0:
                    product.filters = []
                else:
                    filter_options = (self.db.query(FilterOption)
                                     .filter(FilterOption.id.in_(payload.filter_option_ids))
                                     .all())
                    if len(filter_options) != len(payload.filter_option_ids):
                        raise HTTPException(status_code=400, detail="Some filter options not found")
                    product.filters = filter_options
        
        if payload.images is not None:
            self.db.query(ProductImage).filter(ProductImage.product_id == product_id).delete()
            if payload.images:
                self._create_product_images(product.id, payload.images)
        
        if payload.characteristics is not None:
            self.db.query(ProductCharacteristic).filter(ProductCharacteristic.product_id == product_id).delete()
            if payload.characteristics:
                self._create_product_characteristics(product.id, payload.characteristics)
        
        if payload.variations is not None:
            self.db.query(ProductVariation).filter(ProductVariation.product_id == product_id).delete()
            if payload.variations:
                self._create_variations(product.id, payload.variations)
        
        self.db.commit()
        self.db.refresh(product)
        
        # Convert to proper Pydantic response model to avoid serialization issues
        return self._convert_to_response_specific(product)

    def delete(self, product_id: int, vendor_profile_id: str) -> dict:
        """Delete a product"""
        product = self.get_raw(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        if str(product.vendor_profile_id) != str(vendor_profile_id):
            raise HTTPException(status_code=403, detail="Not authorized to delete this product")
        
        try:
            # Remove from basket and favorites
            from sqlalchemy import text
            self.db.execute(text("DELETE FROM basket_items WHERE product_id = :product_id"), {"product_id": product_id})
            self.db.execute(text("DELETE FROM favorites WHERE product_id = :product_id"), {"product_id": product_id})
            
            # Delete product
            self.db.delete(product)
            self.db.commit()
            
            return {"message": "Product deleted successfully"}
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail=f"Failed to delete product: {str(e)}")

    def search_by_filter_options_only(
        self,
        filter_option_ids: List[int],
        match_all: bool = False,
        approved_only: bool = False
    ) -> List[Product]:
        """Search products by filter options only"""
        if not filter_option_ids:
            return []
        
        query = (self.db.query(Product)
                .options(
                    joinedload(Product.category),
                    joinedload(Product.characteristics).joinedload(ProductCharacteristic.type),
                    joinedload(Product.variations).joinedload(ProductVariation.characteristics).joinedload(VariationCharacteristic.type),
                    joinedload(Product.variations).joinedload(ProductVariation.images),
                    joinedload(Product.description_images),
                    joinedload(Product.filters)
                )
                .join(product_filters)
                .filter(product_filters.c.filter_option_id.in_(filter_option_ids)))
        
        # Filter by approval status if requested
        if approved_only:
            query = query.filter(Product.status == 'approved')
        
        if match_all:
            # Products must have ALL specified filter options
            query = (query.group_by(Product.id)
                    .having(func.count(func.distinct(product_filters.c.filter_option_id)) == len(filter_option_ids)))
        
        return query.distinct().all()

    def get_all(self, approved_only: bool = False, category_id: Optional[int] = None, limit: Optional[int] = None, offset: Optional[int] = None, search_query: Optional[str] = None) -> List[Product]:
        """Get all products with optional filtering and pagination"""
        query = (self.db.query(Product)
                .options(
                    joinedload(Product.category),
                    joinedload(Product.characteristics).joinedload(ProductCharacteristic.type),
                    joinedload(Product.variations).joinedload(ProductVariation.characteristics).joinedload(VariationCharacteristic.type),
                    joinedload(Product.variations).joinedload(ProductVariation.images),
                    joinedload(Product.description_images),
                    joinedload(Product.filters)
                ))
        
        # Filter by approval status if requested
        if approved_only:
            query = query.filter(Product.status == 'approved')
        
        # Filter by category if specified
        if category_id is not None:
            query = query.filter(Product.category_id == category_id)
        
        # Add search by name if specified
        if search_query:
            # Use ILIKE for case-insensitive search in PostgreSQL
            query = query.filter(Product.name.ilike(f'%{search_query}%'))
        
        # Add pagination if specified
        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)
        
        return query.all()

    def search_products(
        self,
        search_query: str,
        category_id: Optional[int] = None,
        approved_only: bool = True,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Product]:
        """Search products by name with optional filtering and pagination"""
        query = (self.db.query(Product)
                .options(
                    joinedload(Product.category),
                    joinedload(Product.characteristics).joinedload(ProductCharacteristic.type),
                    joinedload(Product.variations).joinedload(ProductVariation.characteristics).joinedload(VariationCharacteristic.type),
                    joinedload(Product.variations).joinedload(ProductVariation.images),
                    joinedload(Product.description_images),
                    joinedload(Product.filters)
                ))
        
        # Filter by approval status if requested
        if approved_only:
            query = query.filter(Product.status == 'approved')
        
        # Filter by category if specified
        if category_id is not None:
            query = query.filter(Product.category_id == category_id)
        
        # Search by name (case-insensitive)
        if search_query:
            query = query.filter(Product.name.ilike(f'%{search_query}%'))
        
        # Add pagination if specified
        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)
        
        return query.all()

    def get_all_for_admin(
        self, 
        status_filter: Optional[str] = None,
        vendor_id: Optional[int] = None,
        category_id: Optional[int] = None,
        limit: Optional[int] = 100,
        offset: Optional[int] = 0
    ) -> Tuple[List[ProductResponseSpecific], int]:
        """
        Get all products for admin with filtering and pagination
        Returns: (products_list, total_count)
        Includes comprehensive relationships: vendor_profile.user, variations, characteristics, etc.
        """
        query = (self.db.query(Product)
                .options(
                    joinedload(Product.category),
                    joinedload(Product.vendor_profile).joinedload(VendorProfile.user),
                    joinedload(Product.characteristics).joinedload(ProductCharacteristic.type),
                    joinedload(Product.variations).joinedload(ProductVariation.characteristics).joinedload(VariationCharacteristic.type),
                    joinedload(Product.variations).joinedload(ProductVariation.images),
                    joinedload(Product.description_images),
                    joinedload(Product.filters).joinedload(FilterOption.filter_type)
                ))
        
        # Apply filters
        if status_filter:
            query = query.filter(Product.status == status_filter)
        
        if vendor_id:
            query = query.filter(Product.vendor_profile_id == vendor_id)
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination
        products = query.offset(offset).limit(limit).all()
        
        # Convert to response models
        response_products = [self._convert_to_response_specific(product) for product in products]
        
        return response_products, total_count

    def get_product_stats(self) -> dict:
        """
        Get product statistics for the admin dashboard.
        """
        try:
            total_products = self.db.query(Product).count()
            pending_products = self.db.query(Product).filter(Product.status == 'pending').count()
            approved_products = self.db.query(Product).filter(Product.status == 'approved').count()
            rejected_products = self.db.query(Product).filter(Product.status == 'rejected').count()

            current_month = datetime.datetime.utcnow().month
            current_year = datetime.datetime.utcnow().year
            new_products_this_month = self.db.query(Product).filter(
                and_(
                    func.extract('month', Product.created_at) == current_month,
                    func.extract('year', Product.created_at) == current_year
                )
            ).count()

            top_categories_query = self.db.query(
                Category.name,
                func.count(Product.id).label('product_count')
            ).join(Product, Category.id == Product.category_id)\
             .group_by(Category.name)\
             .order_by(func.count(Product.id).desc())\
             .limit(5).all()

            top_categories = [{"category_name": name, "product_count": count} for name, count in top_categories_query]

            return {
                "total_products": total_products,
                "pending_products": pending_products,
                "approved_products": approved_products,
                "rejected_products": rejected_products,
                "new_products_this_month": new_products_this_month,
                "top_categories": top_categories
            }
        except Exception as e:
            logger.error(f"Error getting product stats: {e}")
            return {
                "total_products": 0, "pending_products": 0, "approved_products": 0,
                "rejected_products": 0, "new_products_this_month": 0, "top_categories": []
            }

    def update_product_status(self, product_id: int, new_status: str) -> Product:
        """Update product status (admin only)"""
        
        # Validate status - use lowercase to match database enum
        if new_status not in ['draft', 'pending', 'approved', 'rejected']:
            raise HTTPException(status_code=400, detail=f"Invalid status: {new_status}")
        
        product = self.get_raw(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        old_status = product.status
        product.status = new_status
        
        self.db.commit()
        self.db.refresh(product)
        
        logger.info(f"Product {product_id} status changed from {old_status} to {new_status}")
        return product

    def delete_for_admin(self, product_id: int) -> dict:
        """Delete a product (admin only)"""
        product = self.get_raw(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        try:
            # Remove from basket and favorites
            from sqlalchemy import text
            self.db.execute(text("DELETE FROM basket_items WHERE product_id = :product_id"), {"product_id": product_id})
            self.db.execute(text("DELETE FROM favorites WHERE product_id = :product_id"), {"product_id": product_id})
            
            # Delete product
            self.db.delete(product)
            self.db.commit()
            
            logger.info(f"Product {product_id} deleted by admin")
            return {"message": "Product deleted successfully"}
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail=f"Failed to delete product: {str(e)}")

    def get_pending_products(self, limit: Optional[int] = 100, offset: Optional[int] = 0) -> List[ProductResponseSpecific]:
        """Get all pending products for admin review"""
        products = (self.db.query(Product)
                .options(
                    joinedload(Product.category),
                    joinedload(Product.vendor_profile).joinedload(VendorProfile.user),
                    joinedload(Product.characteristics).joinedload(ProductCharacteristic.type),
                    joinedload(Product.variations).joinedload(ProductVariation.characteristics).joinedload(VariationCharacteristic.type),
                    joinedload(Product.variations).joinedload(ProductVariation.images),
                    joinedload(Product.description_images),
                    joinedload(Product.filters).joinedload(FilterOption.filter_type)
                )
                .filter(Product.status == 'pending')
                .offset(offset)
                .limit(limit)
                .all())
        
        # Convert to response models
        return [self._convert_to_response_specific(product) for product in products]

    def get_pending_products_count(self) -> int:
        """Get total count of pending products"""
        return self.db.query(Product).filter(Product.status == 'pending').count()

    def _convert_to_response_specific(self, product: Product) -> ProductResponseSpecific:
        """Convert SQLAlchemy Product model to ProductResponseSpecific Pydantic model"""
        
        # Convert category
        category = None
        if product.category:
            category = CategoryResponse(
                id=product.category.id,
                name=product.category.name
            )
        
        # Convert vendor profile
        vendor_profile = None
        if product.vendor_profile:
            user = None
            if product.vendor_profile.user:
                user = UserResponse(
                    id=product.vendor_profile.user.id,
                    first_name=product.vendor_profile.user.first_name,
                    last_name=product.vendor_profile.user.last_name,
                    email=product.vendor_profile.user.email,
                    phone=product.vendor_profile.user.phone
                )
            
            vendor_profile = ProductVendorProfileResponse(
                id=product.vendor_profile.id,
                user_id=product.vendor_profile.user_id,
                business_name=product.vendor_profile.business_name,
                business_type=product.vendor_profile.business_type.value if product.vendor_profile.business_type else None,
                status=product.vendor_profile.status.value if product.vendor_profile.status else None,
                contact_phone=getattr(product.vendor_profile, 'contact_phone', None),
                contact_email=getattr(product.vendor_profile, 'contact_email', None),
                description=product.vendor_profile.description,
                user=user
            )
        
        # Convert description images
        description_images = []
        if product.description_images:
            for img in product.description_images:
                description_images.append(ProductImageResponse(
                    id=img.id,
                    product_id=img.product_id,
                    url=img.url,
                    alt_text=img.alt_text,
                    order=img.order
                ))
        
        # Convert filters
        filters = []
        if product.filters:
            for filter_option in product.filters:
                filter_type_data = None
                if hasattr(filter_option, 'filter_type') and filter_option.filter_type:
                    filter_type_data = {
                        "id": filter_option.filter_type.id,
                        "name": filter_option.filter_type.name,
                        "category_id": filter_option.filter_type.category_id
                    }
                
                filters.append(FilterOptionResponse(
                    id=filter_option.id,
                    value=filter_option.value,
                    filter_type=filter_type_data
                ))
        
        # Convert characteristics
        characteristics = []
        if product.characteristics:
            for char in product.characteristics:
                type_data = None
                if char.type:
                    type_data = {
                        "id": char.type.id,
                        "name": char.type.name
                    }
                
                characteristics.append(CharacteristicResponse(
                    id=char.id,
                    characteristic_type_id=char.characteristic_type_id,
                    value=char.value,
                    type_name=char.type.name if char.type else "",
                    type=type_data
                ))
        
        # Convert variations
        variations = []
        if product.variations:
            for variation in product.variations:
                # Convert variation characteristics
                var_characteristics = []
                if variation.characteristics:
                    for var_char in variation.characteristics:
                        var_type_data = None
                        if var_char.type:
                            var_type_data = {
                                "id": var_char.type.id,
                                "name": var_char.type.name
                            }
                        
                        var_characteristics.append(CharacteristicResponse(
                            id=var_char.id,
                            characteristic_type_id=var_char.characteristic_type_id,
                            value=var_char.value,
                            type_name=var_char.type.name if var_char.type else "",
                            type=var_type_data
                        ))
                
                # Convert variation images
                var_images = []
                if variation.images:
                    for var_img in variation.images:
                        var_images.append(VariationImageResponse(
                            id=var_img.id,
                            variation_id=var_img.variation_id,
                            url=var_img.url,
                            alt_text=var_img.alt_text,
                            order=var_img.order
                        ))
                
                variations.append(VariationResponse(
                    id=variation.id,
                    product_id=variation.product_id,
                    name=variation.name,
                    price=float(variation.price),
                    sku=variation.sku,
                    status=variation.status,
                    quantity=variation.quantity,
                    created_at=variation.created_at.isoformat(),
                    characteristics=var_characteristics,
                    images=var_images
                ))
        
        # Get favorites count (placeholder for now)
        favorites_count = 0
        
        return ProductResponseSpecific(
            id=product.id,
            vendor_profile_id=product.vendor_profile_id,
            category_id=product.category_id,
            name=product.name,
            description=product.description,
            main_image_url=product.main_image_url,
            price=float(product.price),
            status=product.status,
            quantity=product.quantity,
            created_at=product.created_at.isoformat(),
            updated_at=product.updated_at.isoformat(),
            category=category,
            vendor_profile=vendor_profile,
            description_images=description_images,
            filters=filters,
            characteristics=characteristics,
            variations=variations,
            favorites_count=favorites_count
        )
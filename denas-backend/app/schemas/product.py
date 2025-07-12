from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import enum

from .product_image import ProductImageCreate

class AvailabilityType(enum.Enum):
    IN_STOCK = "in_stock"
    PRE_ORDER = "pre_order"
    DISCONTINUED = "discontinued"


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    stock_quantity: int = Field(0, ge=0)
    availability_type: AvailabilityType = AvailabilityType.IN_STOCK
    preorder_available_date: Optional[datetime] = None
    is_active: bool = True
    category_id: int


class ProductCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: str | None = None
    price: Decimal = Field(..., gt=0)
    stock_quantity: int = Field(0, ge=0)
    availability_type: AvailabilityType = AvailabilityType.IN_STOCK
    preorder_available_date: datetime | None = None
    is_active: bool = True
    category_id: int
    images: List[ProductImageCreate] = []  # Accept a list of images


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    availability_type: Optional[AvailabilityType] = None
    preorder_available_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    category_id: Optional[int] = None


class ProductInDB(ProductBase):
    id: int
    created_at: datetime

    @field_validator('availability_type', mode='before')
    @classmethod
    def validate_availability_type_field(cls, v):
        if hasattr(v, 'value'):
            return v.value
        return v

    class Config:
        from_attributes = True


class Product(ProductInDB):
    pass


# Category response schemas
class CategoryResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class CategoryCatalog(BaseModel):
    """Lightweight category info for catalog views"""
    id: int
    name: str

    class Config:
        from_attributes = True


# Product image response schemas
class ProductImageResponse(BaseModel):
    id: int
    product_id: int
    image_url: str
    image_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class ProductImageCatalog(BaseModel):
    """Lightweight image info for catalog views"""
    id: int
    image_url: str
    image_type: str

    class Config:
        from_attributes = True


# CATALOG SCHEMAS - Lightweight for product listings/browsing
class ProductCatalog(BaseModel):
    """
    Lightweight product schema for catalog/listing views
    Contains only essential info: id, name, price, basic image, availability
    """
    id: int
    name: str
    price: Decimal
    availability_type: AvailabilityType
    is_active: bool
    
    # Minimal related data
    category: Optional[CategoryCatalog] = None
    # Only first/primary image for catalog view
    primary_image: Optional[ProductImageCatalog] = None
    favorites_count: Optional[int] = 0

    @field_validator('availability_type', mode='before')
    @classmethod
    def validate_availability_type_field(cls, v):
        if hasattr(v, 'value'):
            return v.value
        return v

    class Config:
        from_attributes = True


# DETAILED SCHEMAS - Full data for specific product views
class ProductResponseSpecific(BaseModel):
    """
    Comprehensive product schema for detailed/specific product views
    Contains full product information with all related data
    """
    id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    stock_quantity: int
    availability_type: AvailabilityType
    preorder_available_date: Optional[datetime] = None
    is_active: bool
    category_id: int
    created_at: datetime
    
    # Full related objects with complete data
    category: Optional[CategoryResponse] = None
    images: List[ProductImageResponse] = []
    favorites_count: Optional[int] = 0

    @field_validator('availability_type', mode='before')
    @classmethod
    def validate_availability_type_field(cls, v):
        if hasattr(v, 'value'):
            return v.value
        return v

    class Config:
        from_attributes = True


# Keep existing comprehensive response for backward compatibility
class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    stock_quantity: int
    availability_type: AvailabilityType
    preorder_available_date: Optional[datetime] = None
    is_active: bool
    category_id: int
    created_at: datetime
    
    # Full related objects, not just references
    category: Optional[CategoryResponse] = None
    images: List[ProductImageResponse] = []
    favorites_count: Optional[int] = 0

    @field_validator('availability_type', mode='before')
    @classmethod
    def validate_availability_type_field(cls, v):
        if hasattr(v, 'value'):
            return v.value
        return v

    class Config:
        from_attributes = True


# Legacy schemas - keeping for backward compatibility
class ProductWithImages(ProductInDB):
    images: List[dict] = []
    image_urls: List[str] = []

    class Config:
        from_attributes = True


class ProductWithCategory(ProductInDB):
    category: Optional[dict] = None

    class Config:
        from_attributes = True


class ProductWithDetails(ProductInDB):
    category: Optional[dict] = None
    images: List[dict] = []
    image_urls: List[str] = []
    favorites_count: Optional[int] = 0

    class Config:
        from_attributes = True
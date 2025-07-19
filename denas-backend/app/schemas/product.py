from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import enum


class AvailabilityType(enum.Enum):
    IN_STOCK = "IN_STOCK"
    PRE_ORDER = "PRE_ORDER"
    DISCONTINUED = "DISCONTINUED"


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0, decimal_places=2)
    stock_quantity: int = Field(default=0, ge=0)
    availability_type: AvailabilityType = AvailabilityType.IN_STOCK
    preorder_available_date: Optional[datetime] = None
    is_active: bool = True
    category_id: int = Field(..., gt=0)


class ProductCreate(ProductBase):
    image_urls: Optional[List[str]] = []  # URLs for product images


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    stock_quantity: Optional[int] = Field(None, ge=0)
    availability_type: Optional[AvailabilityType] = None
    preorder_available_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    category_id: Optional[int] = Field(None, gt=0)
    image_urls: Optional[List[str]] = []  # URLs for product images


class ProductInDB(ProductBase):
    id: int
    created_at: datetime

    @field_validator('availability_type', mode='before')
    @classmethod
    def validate_availability_type(cls, v):
        if hasattr(v, 'value'):
            return v.value
        return v

    class Config:
        from_attributes = True


class Product(ProductInDB):
    pass


class ProductResponse(ProductInDB):
    """Alternative name for Product for backward compatibility"""
    pass


class ProductCatalog(BaseModel):
    """Simplified product model for catalog listings"""
    id: int
    name: str
    price: Decimal
    image_url: Optional[str] = None  # Primary image URL
    availability_type: AvailabilityType
    is_active: bool
    category_id: int

    @field_validator('availability_type', mode='before')
    @classmethod
    def validate_availability_type(cls, v):
        if hasattr(v, 'value'):
            return v.value
        return v

    class Config:
        from_attributes = True


class ProductWithDetails(ProductInDB):
    """Product with all related data for detailed view"""
    category: Optional["Category"] = None
    images: List["ProductImage"] = []

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Response model for paginated product lists"""
    items: List[ProductCatalog]
    total: int
    page: int
    size: int
    has_next: bool
    has_previous: bool

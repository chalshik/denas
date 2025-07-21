from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import enum


class AvailabilityType(enum.Enum):
    IN_STOCK = "IN_STOCK"
    PRE_ORDER = "PRE_ORDER"


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0, decimal_places=2)
    stock_quantity: int = Field(default=0, ge=0)
    availability_type: str = "IN_STOCK"  # Change to string type
    preorder_available_date: Optional[datetime] = None
    is_active: bool = True
    category_id: int = Field(..., gt=0)
    
    @field_validator('availability_type', mode='before')
    @classmethod
    def validate_availability_type(cls, v):
        """Convert enum to string value for database storage"""
        if isinstance(v, AvailabilityType):
            return v.value
        if isinstance(v, str):
            # Validate that the string is a valid enum value
            try:
                AvailabilityType(v)  # Just validate, don't convert
                return v
            except ValueError:
                raise ValueError(f"Invalid availability type: {v}")
        return v


class ProductCreate(ProductBase):
    image_urls: Optional[List[str]] = []  # URLs for product images


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    stock_quantity: Optional[int] = Field(None, ge=0)
    availability_type: Optional[str] = None  # Change to string type
    preorder_available_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    category_id: Optional[int] = Field(None, gt=0)
    image_urls: Optional[List[str]] = []  # URLs for product images
    
    @field_validator('availability_type', mode='before')
    @classmethod
    def validate_availability_type(cls, v):
        """Convert enum to string value for database storage"""
        if v is None:
            return v
        if isinstance(v, AvailabilityType):
            return v.value
        if isinstance(v, str):
            # Validate that the string is a valid enum value
            try:
                AvailabilityType(v)  # Just validate, don't convert
                return v
            except ValueError:
                raise ValueError(f"Invalid availability type: {v}")
        return v


class ProductInDB(ProductBase):
    id: int
    created_at: datetime

    @field_validator('availability_type', mode='before')
    @classmethod
    def validate_availability_type(cls, v):
        """Convert enum to string value for database storage"""
        if isinstance(v, AvailabilityType):
            return v.value
        if isinstance(v, str):
            return v
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
    availability_type: str  # Change to string type
    is_active: bool
    category_id: int
    is_favorited: Optional[bool] = None  # Whether current user has favorited this product

    @field_validator('availability_type', mode='before')
    @classmethod
    def validate_availability_type(cls, v):
        """Convert enum to string value for database storage"""
        if isinstance(v, AvailabilityType):
            return v.value
        if isinstance(v, str):
            return v
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


class AdminProductListResponse(BaseModel):
    """Response model for paginated admin product lists with full details"""
    items: List[ProductWithDetails]
    total: int
    page: int
    size: int
    has_next: bool
    has_previous: bool

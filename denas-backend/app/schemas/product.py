from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import enum


class AvailabilityType(enum.Enum):
    IN_STOCK = "in_stock"
    PRE_ORDER = "pre_order"
    DISCONTINUED = "discontinued"


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0, decimal_places=2)
    stock_quantity: int = Field(0, ge=0)
    availability_type: AvailabilityType = AvailabilityType.IN_STOCK
    preorder_available_date: Optional[datetime] = None
    is_active: bool = True
    category_id: int


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    stock_quantity: Optional[int] = Field(None, ge=0)
    availability_type: Optional[AvailabilityType] = None
    preorder_available_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    category_id: Optional[int] = None


class ProductInDB(ProductBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Product(ProductInDB):
    pass


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
from pydantic import BaseModel, Field, computed_field
from typing import Optional
from decimal import Decimal

from .product import ProductResponse


class ShoppingCartItemBase(BaseModel):
    cart_id: int
    product_id: int
    quantity: int = Field(..., gt=0)


class ShoppingCartItemCreate(BaseModel):
    """Schema for creating a new cart item"""
    product_id: int
    quantity: int = Field(..., gt=0, description="Quantity must be greater than 0")


class ShoppingCartItemUpdate(BaseModel):
    """Schema for updating cart item quantity"""
    quantity: int = Field(..., gt=0, description="Quantity must be greater than 0")


class ShoppingCartItemInDB(ShoppingCartItemBase):
    id: int

    class Config:
        from_attributes = True


class ShoppingCartItem(ShoppingCartItemInDB):
    """Basic cart item without relationships"""
    pass


class ShoppingCartItemWithProduct(ShoppingCartItemInDB):
    """Cart item with full product details"""
    product: ProductResponse
    
    @computed_field
    @property
    def subtotal(self) -> float:
        """Calculate subtotal for this item"""
        return float(self.product.price * self.quantity)

    class Config:
        from_attributes = True 
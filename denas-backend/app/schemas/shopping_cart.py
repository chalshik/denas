from pydantic import BaseModel, Field, computed_field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

from .product import ProductResponse


class ShoppingCartBase(BaseModel):
    user_id: int


class ShoppingCartCreate(ShoppingCartBase):
    pass


class ShoppingCartUpdate(BaseModel):
    pass  # No updates needed for shopping cart, only create/delete


class ShoppingCartInDB(ShoppingCartBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ShoppingCart(ShoppingCartInDB):
    pass


class ShoppingCartItemResponse(BaseModel):
    """Cart item with full product details"""
    id: int
    cart_id: int
    product_id: int
    quantity: int
    product: ProductResponse
    
    @computed_field
    @property
    def subtotal(self) -> float:
        """Calculate subtotal for this item"""
        return float(self.product.price * self.quantity)
    
    class Config:
        from_attributes = True


class ShoppingCartResponse(ShoppingCartInDB):
    """Shopping cart with items and computed totals"""
    cart_items: List[ShoppingCartItemResponse] = []
    
    @computed_field
    @property
    def total_items(self) -> int:
        """Total number of items (sum of quantities)"""
        return sum(item.quantity for item in self.cart_items)
    
    @computed_field
    @property
    def total_price(self) -> float:
        """Total price of all items"""
        return sum(item.subtotal for item in self.cart_items)
    
    @computed_field
    @property
    def items_count(self) -> int:
        """Number of different products in cart"""
        return len(self.cart_items)

    class Config:
        from_attributes = True


class ShoppingCartSummary(BaseModel):
    """Cart summary without full item details"""
    total_items: int
    total_price: float
    items_count: int
    cart_id: Optional[int] = None


class CartActionResponse(BaseModel):
    """Response for cart actions (add, update, remove)"""
    success: bool
    message: str
    item_id: Optional[int] = None
    quantity: Optional[int] = None
    new_quantity: Optional[int] = None
    old_quantity: Optional[int] = None
    action: Optional[str] = None


class CartClearResponse(BaseModel):
    """Response for cart clear action"""
    success: bool
    message: str
    items_removed: int 
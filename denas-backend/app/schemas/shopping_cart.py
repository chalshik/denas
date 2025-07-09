from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


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


class ShoppingCartWithItems(ShoppingCartInDB):
    cart_items: Optional[List[dict]] = []
    total_items: Optional[int] = 0
    total_price: Optional[float] = 0.0

    class Config:
        from_attributes = True


class ShoppingCartWithUser(ShoppingCartInDB):
    user: Optional[dict] = None

    class Config:
        from_attributes = True 
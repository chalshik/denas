from pydantic import BaseModel, Field
from typing import Optional


class ShoppingCartItemBase(BaseModel):
    cart_id: int
    product_id: int
    quantity: int = Field(..., gt=0)


class ShoppingCartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class ShoppingCartItemUpdate(BaseModel):
    quantity: Optional[int] = Field(None, gt=0)


class ShoppingCartItemInDB(ShoppingCartItemBase):
    id: int

    class Config:
        from_attributes = True


class ShoppingCartItem(ShoppingCartItemInDB):
    pass


class ShoppingCartItemWithProduct(ShoppingCartItemInDB):
    product: Optional[dict] = None
    subtotal: Optional[float] = None

    class Config:
        from_attributes = True


class ShoppingCartItemWithCart(ShoppingCartItemInDB):
    cart: Optional[dict] = None

    class Config:
        from_attributes = True 
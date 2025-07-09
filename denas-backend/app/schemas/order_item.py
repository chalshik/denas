from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


class OrderItemBase(BaseModel):
    order_id: int
    product_id: int
    quantity: int = Field(..., gt=0)
    price: Decimal = Field(..., gt=0, decimal_places=2)  # Price at time of order


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    # price will be fetched from product at order time


class OrderItemUpdate(BaseModel):
    quantity: Optional[int] = Field(None, gt=0)
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)


class OrderItemInDB(OrderItemBase):
    id: int

    class Config:
        from_attributes = True


class OrderItem(OrderItemInDB):
    pass


class OrderItemWithProduct(OrderItemInDB):
    product: Optional[dict] = None

    class Config:
        from_attributes = True


class OrderItemWithOrder(OrderItemInDB):
    order: Optional[dict] = None

    class Config:
        from_attributes = True 
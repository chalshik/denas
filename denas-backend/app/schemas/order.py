from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import enum


class OrderStatus(enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class OrderBase(BaseModel):
    user_id: int
    status: OrderStatus = OrderStatus.PENDING
    total_price: Decimal = Field(..., gt=0, decimal_places=2)


class OrderCreate(BaseModel):
    user_id: int
    # total_price will be calculated from order items


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    total_price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)


class OrderInDB(OrderBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Order(OrderInDB):
    pass


class OrderWithItems(OrderInDB):
    order_items: Optional[List[dict]] = []
    payments: Optional[List[dict]] = []

    class Config:
        from_attributes = True


class OrderWithUser(OrderInDB):
    user: Optional[dict] = None

    class Config:
        from_attributes = True 
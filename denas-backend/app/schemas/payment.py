from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
import enum


class PaymentStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentBase(BaseModel):
    order_id: int
    amount: Decimal = Field(..., gt=0)
    payment_method: str = Field(..., min_length=1, max_length=50)
    status: PaymentStatus = PaymentStatus.PENDING


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, gt=0)
    payment_method: Optional[str] = Field(None, min_length=1, max_length=50)
    status: Optional[PaymentStatus] = None


class PaymentInDB(PaymentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Payment(PaymentInDB):
    pass


class PaymentWithOrder(PaymentInDB):
    order: Optional[dict] = None

    class Config:
        from_attributes = True 
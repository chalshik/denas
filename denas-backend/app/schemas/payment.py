from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
import enum


class PaymentStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class PaymentBase(BaseModel):
    order_id: int
    payment_provider: str = Field(..., max_length=50)
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    status: PaymentStatus = PaymentStatus.PENDING


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    payment_provider: Optional[str] = Field(None, max_length=50)
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
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
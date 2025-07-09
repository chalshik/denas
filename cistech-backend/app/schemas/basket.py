from pydantic import BaseModel, Field, computed_field
from typing import List, Optional
from datetime import datetime
from .product import ProductResponse

class BasketItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1, description="Quantity must be at least 1")

class BasketItemCreate(BasketItemBase):
    pass

class BasketItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1, description="Quantity must be at least 1")

class BasketItemResponse(BasketItemBase):
    id: int
    basket_id: int
    product: ProductResponse
    
    @computed_field
    @property
    def total_price(self) -> float:
        return float(self.quantity * self.product.price)
    
    model_config = {"from_attributes": True}

class BasketResponse(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    items: List[BasketItemResponse] = []
    
    @computed_field
    @property
    def total_quantity(self) -> int:
        return sum(item.quantity for item in self.items)
    
    @computed_field
    @property
    def total_price(self) -> float:
        return sum(item.total_price for item in self.items)
    
    model_config = {"from_attributes": True}
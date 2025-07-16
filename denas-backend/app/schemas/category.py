from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)


class CategoryInDB(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Category(CategoryInDB):
    pass


class CategoryWithProducts(CategoryInDB):
    products: List["Product"] = []

    class Config:
        from_attributes = True


# Avoid circular import by using forward reference
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.schemas.product import Product

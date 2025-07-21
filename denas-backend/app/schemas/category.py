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


class CategoryWithMetadata(CategoryInDB):
    can_delete: bool = True
    product_count: Optional[int] = None

    class Config:
        from_attributes = True


class CategoryWithProducts(CategoryInDB):
    products: List["Product"] = []

    class Config:
        from_attributes = True

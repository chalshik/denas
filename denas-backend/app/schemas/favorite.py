from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class FavoriteBase(BaseModel):
    user_id: int
    product_id: int


class FavoriteCreate(BaseModel):
    product_id: int  # Only product_id needed, user_id will be set from auth


class FavoriteUpdate(BaseModel):
    pass  # No updates needed for favorites, only create/delete


class FavoriteInDB(FavoriteBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Favorite(FavoriteInDB):
    pass


# Schemas for detailed responses with related data
class FavoriteWithProduct(FavoriteInDB):
    product: Optional[dict] = None  # Will be populated with product details

    class Config:
        from_attributes = True


class FavoriteWithUser(FavoriteInDB):
    user: Optional[dict] = None  # Will be populated with user details

    class Config:
        from_attributes = True 
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import enum


class ImageType(enum.Enum):
    OFFICIAL = "official"
    RECEIVED = "received"
    OTHER = "other"


class ProductImageBase(BaseModel):
    product_id: int
    image_url: str = Field(..., max_length=255)
    image_type: ImageType = ImageType.OFFICIAL


class ProductImageCreate(BaseModel):
    image_url: str = Field(..., max_length=255)
    image_type: ImageType = ImageType.OFFICIAL

class ProductImageUpdate(BaseModel):
    image_url: Optional[str] = Field(None, max_length=255)
    image_type: Optional[ImageType] = None


class ProductImageInDB(ProductImageBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ProductImage(ProductImageInDB):
    pass


class ProductImageWithProduct(ProductImageInDB):
    # Remove product field to avoid circular import
    # Product information can be fetched separately if needed
    pass

    class Config:
        from_attributes = True 
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, TYPE_CHECKING
from datetime import datetime
import enum

if TYPE_CHECKING:
    from app.schemas.product import Product


class ImageType(enum.Enum):
    OFFICIAL = "official"
    RECEIVED = "received"
    OTHER = "other"


class ProductImageBase(BaseModel):
    product_id: int
    image_url: str = Field(..., max_length=255)
    image_type: ImageType = ImageType.OFFICIAL


class ProductImageCreate(ProductImageBase):
    pass


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
    product: Optional["Product"] = None

    class Config:
        from_attributes = True


# Rebuild model to resolve forward references
# Import Product for runtime use
from app.schemas.product import Product
ProductImageWithProduct.model_rebuild() 
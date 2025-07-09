from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base import Base

class ImageType(enum.Enum):
    OFFICIAL = "official"
    RECEIVED = "received"
    OTHER = "other"

class ProductImage(Base):
    __tablename__ = "product_images"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    image_url = Column(String(255), nullable=False)
    image_type = Column(Enum(ImageType), default=ImageType.OFFICIAL)
    created_at = Column(TIMESTAMP, default=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="images")
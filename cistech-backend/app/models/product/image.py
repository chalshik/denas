from sqlalchemy import (
    Column, Integer, String, ForeignKey
)
from sqlalchemy.orm import relationship
from app.database import Base

class ProductImage(Base):
    __tablename__ = 'product_images'

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    url = Column(String(500), nullable=False)
    alt_text = Column(String(255), nullable=True)
    order = Column(Integer, default=0)

    product = relationship('Product', back_populates='description_images')

# Картинки для вариаций
class VariationImage(Base):
    __tablename__ = 'variation_images'

    id = Column(Integer, primary_key=True, index=True)
    variation_id = Column(Integer, ForeignKey('product_variations.id'), nullable=False)
    url = Column(String(500), nullable=False)
    alt_text = Column(String(255), nullable=True)
    order = Column(Integer, default=0)

    variation = relationship('ProductVariation', back_populates='images')
from sqlalchemy import (
    Column, Integer, String, ForeignKey
)
from sqlalchemy.orm import relationship
from app.database import Base

class CharacteristicType(Base):
    __tablename__ = 'characteristic_types'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)

    characteristics = relationship('VariationCharacteristic', back_populates='type')
    product_characteristics = relationship('ProductCharacteristic', back_populates='type')

# Характеристики основного продукта
class ProductCharacteristic(Base):
    __tablename__ = 'product_characteristics'

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    characteristic_type_id = Column(Integer, ForeignKey('characteristic_types.id'), nullable=False)
    value = Column(String(255), nullable=False)

    product = relationship('Product', back_populates='characteristics')
    type = relationship('CharacteristicType', back_populates='product_characteristics')

# Характеристики вариаций
class VariationCharacteristic(Base):
    __tablename__ = 'variation_characteristics'

    id = Column(Integer, primary_key=True, index=True)
    variation_id = Column(Integer, ForeignKey('product_variations.id'), nullable=False)
    characteristic_type_id = Column(Integer, ForeignKey('characteristic_types.id'), nullable=False)
    value = Column(String(255), nullable=False)

    variation = relationship('ProductVariation', back_populates='characteristics')
    type = relationship('CharacteristicType', back_populates='characteristics')
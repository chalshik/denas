# app/models/basket_item.py
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, validates
from app.database import Base

class BasketItem(Base):
    __tablename__ = 'basket_items'
    id = Column(Integer, primary_key=True, index=True)
    basket_id = Column(Integer, ForeignKey('baskets.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)

    basket = relationship('Basket', back_populates='items')
    product = relationship('Product', back_populates='basket_items')

    @validates('quantity')
    def validate_quantity(self, key, value):
        if value < 1:
            raise ValueError('Quantity must be at least 1')
        return value

# app/models/basket.py
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from app.database import Base

class Basket(Base):
    __tablename__ = 'baskets'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship('User', back_populates='basket', uselist=False)
    items = relationship(
        'BasketItem',
        back_populates='basket',
        cascade='all, delete-orphan',
        lazy='joined'
    )

    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items)

    @property
    def total_price(self):
        return sum(item.quantity * item.product.price for item in self.items)

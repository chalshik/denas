# models.py - SQLAlchemy Database Models
from sqlalchemy import Column, Integer, String, Text, DECIMAL, Boolean, TIMESTAMP, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime
from app.db.base import Base

class AvailabilityType(enum.Enum):
    IN_STOCK = "IN_STOCK"
    PRE_ORDER = "PRE_ORDER"
    
    def __str__(self):
        return self.value

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2), nullable=False)
    stock_quantity = Column(Integer, default=0)
    availability_type = Column(String(20), default="IN_STOCK")
    preorder_available_date = Column(TIMESTAMP, nullable=True)
    is_active = Column(Boolean, default=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    created_at = Column(TIMESTAMP, default=func.now())
    
    # Relationships
    category = relationship("Category", back_populates="products")
    images = relationship("ProductImage", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
    cart_items = relationship("ShoppingCartItem", back_populates="product")
    favorites = relationship("Favorite", back_populates="product", cascade="all, delete-orphan")

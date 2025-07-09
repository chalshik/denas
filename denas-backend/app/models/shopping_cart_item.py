from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class ShoppingCartItem(Base):
    __tablename__ = "shopping_cart_items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cart_id = Column(Integer, ForeignKey("shopping_carts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    
    # Relationships
    cart = relationship("ShoppingCart", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")

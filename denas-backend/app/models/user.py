from sqlalchemy import Column, Integer, String, Text, DECIMAL, Boolean, TIMESTAMP, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base import Base

class UserRole(enum.Enum):
    USER = "User"
    ADMIN = "Admin"
    MANAGER = "Manager"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(String(100), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    created_at = Column(TIMESTAMP, default=func.now())
    
    # Relationships
    orders = relationship("Order", back_populates="user")
    shopping_cart = relationship("ShoppingCart", back_populates="user", uselist=False)
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
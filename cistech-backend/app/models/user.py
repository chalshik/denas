from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class UserType(enum.Enum):
    USER = "USER"
    VENDOR = "VENDOR"
    ADMIN = "ADMIN"
    SUPERADMIN = "SUPERADMIN"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    firebase_uid = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    user_type = Column(Enum(UserType), default=UserType.USER, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship
    vendor_profile = relationship("VendorProfile", back_populates="user", uselist=False) 
    favorites = relationship(
        'Favorite',
        back_populates='user',
        cascade='all, delete-orphan'
    )
    favorite_products = relationship(
        'Product',
        secondary='favorites',
        back_populates='favorited_by'
    )

    basket = relationship('Basket', back_populates='user', uselist=False)
    
    # Helper methods for admin checking
    def is_admin(self) -> bool:
        """Check if user is an admin or superadmin"""
        return self.user_type in [UserType.ADMIN, UserType.SUPERADMIN]
    
    def is_superadmin(self) -> bool:
        """Check if user is a superadmin"""
        return self.user_type == UserType.SUPERADMIN
    
    def can_manage_users(self) -> bool:
        """Check if user can manage other users"""
        return self.user_type == UserType.SUPERADMIN
    
    def can_manage_vendors(self) -> bool:
        """Check if user can manage vendors"""
        return self.user_type in [UserType.ADMIN, UserType.SUPERADMIN]
    
    def can_manage_products(self) -> bool:
        """Check if user can manage products"""
        return self.user_type in [UserType.ADMIN, UserType.SUPERADMIN]

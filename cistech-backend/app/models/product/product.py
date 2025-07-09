from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey,
    DECIMAL, DateTime, Boolean, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# Определим перечисление для статуса (если нужен более гибкий статус, 
# например pending/approved/rejected/draft)
product_status_enum = Enum(
    'draft',      # черновик
    'pending',    # ожидает одобрения
    'approved',   # одобрен
    'rejected',   # отклонён
    name='product_status'
)

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    vendor_profile_id = Column(Integer, ForeignKey('vendor_profiles.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    main_image_url = Column(String(500), nullable=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    
    # --- Новые поля ---
    status = Column(
        product_status_enum,
        nullable=False,
        server_default='approved',  # Changed from 'pending' to 'approved'
        comment='pending/approved/rejected'
    )
    quantity = Column(
        Integer,
        nullable=False,
        server_default='0',
        comment='Общее количество товара на складе'
    )
    # --------------------

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    vendor_profile = relationship('VendorProfile', back_populates='products')
    category = relationship('Category', back_populates='products')
    variations = relationship(
        'ProductVariation',
        back_populates='product',
        cascade='all, delete-orphan'
    )
    filters = relationship(
        'FilterOption',
        secondary='product_filters',
        back_populates='products'
    )
    description_images = relationship(
        'ProductImage',
        back_populates='product',
        cascade='all, delete-orphan'
    )
    characteristics = relationship(
        'ProductCharacteristic',
        back_populates='product',
        cascade='all, delete-orphan'
    )

    favorited_by = relationship(
        'User',
        secondary='favorites',
        back_populates='favorite_products'
    )

    favorites = relationship(
        'Favorite',
        back_populates='product',
        cascade='all, delete-orphan'
    )

    basket_items = relationship('BasketItem', back_populates='product')

class ProductVariation(Base):
    __tablename__ = 'product_variations'

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    sku = Column(String(100), unique=True, index=True, nullable=True)
    name = Column(String(255), nullable=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    
    # --- Новые поля ---
    status = Column(
        product_status_enum,
        nullable=False,
        server_default='approved',  # Changed from 'pending' to 'approved'
        comment='pending/approved/rejected'
    )
    quantity = Column(
        Integer,
        nullable=False,
        server_default='0',
        comment='Количество единиц этой вариации в наличии'
    )
    # --------------------

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship('Product', back_populates='variations')
    characteristics = relationship(
        'VariationCharacteristic',
        back_populates='variation',
        cascade='all, delete-orphan'
    )
    images = relationship(
        'VariationImage',
        back_populates='variation',
        cascade='all, delete-orphan'
    )
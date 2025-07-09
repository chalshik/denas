from sqlalchemy import (
    Column, Integer, String, ForeignKey, Table, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.database import Base

# Таблица связей для фильтров
product_filters = Table(
    'product_filters', Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id'), primary_key=True),
    Column('filter_option_id', Integer, ForeignKey('filter_options.id'), primary_key=True)
)

# Типы фильтров и опции
class FilterType(Base):
    __tablename__ = 'filter_types'

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    name = Column(String(255), nullable=False)

    # Составное ограничение уникальности - комбинация категории и названия должна быть уникальной
    __table_args__ = (
        UniqueConstraint('category_id', 'name', name='uq_filter_type_category_name'),
    )

    category = relationship('Category', back_populates='filter_types')
    options = relationship('FilterOption', back_populates='filter_type')

class FilterOption(Base):
    __tablename__ = 'filter_options'

    id = Column(Integer, primary_key=True, index=True)
    filter_type_id = Column(Integer, ForeignKey('filter_types.id'), nullable=False)
    value = Column(String(255), nullable=False)

    filter_type = relationship('FilterType', back_populates='options')
    products = relationship('Product', secondary=product_filters, back_populates='filters')

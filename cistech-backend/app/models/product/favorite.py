from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint, func
from sqlalchemy.orm import relationship
from app.database import Base

class Favorite(Base):
    __tablename__ = 'favorites'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (
        UniqueConstraint('user_id', 'product_id', name='uq_user_product_favorite'),
    )

    user    = relationship('User',    back_populates='favorites')
    product = relationship('Product', back_populates='favorites')

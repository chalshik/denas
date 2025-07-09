from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from app import models
from app.schemas.favorite import FavoriteCreate
from app.schemas.product import ProductResponse
from typing import List

def get_user_favorites(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[models.Favorite]:
    """List a user's favorites, newest first."""
    return (
        db.query(models.Favorite)
          .filter(models.Favorite.user_id == user_id)
          .order_by(models.Favorite.created_at.desc())
          .offset(skip)
          .limit(limit)
          .all()
    )

def get_user_favorite_products(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[ProductResponse]:
    """Get all favorite products for a user with full product details."""
    # Simple query to get products that are in user's favorites
    favorite_products = (
        db.query(models.Product)
          .join(models.Favorite, models.Product.id == models.Favorite.product_id)
          .filter(models.Favorite.user_id == user_id)
          .filter(models.Product.status == 'approved')  # Only approved products
          .order_by(models.Favorite.created_at.desc())
          .offset(skip)
          .limit(limit)
          .all()
    )
    
    # Convert to ProductResponse
    products = []
    for product in favorite_products:
        products.append(ProductResponse(
            id=product.id,
            name=product.name,
            description=product.description,
            main_image_url=product.main_image_url,
            price=float(product.price),
            status=product.status,
            quantity=product.quantity,
            vendor_profile_id=product.vendor_profile_id,
            category_id=product.category_id
        ))
    
    return products

def get_favorite(
    db: Session, user_id: int, product_id: int
) -> models.Favorite | None:
    """Fetch one favorite entry (or None)."""
    return (
        db.query(models.Favorite)
          .filter_by(user_id=user_id, product_id=product_id)
          .first()
    )

def create_favorite(
    db: Session, user_id: int, fav_in: FavoriteCreate
) -> models.Favorite:
    """Idempotently add a favorite, 404 if product missing."""
    existing = get_favorite(db, user_id, fav_in.product_id)
    if existing:
        return existing

    if not db.get(models.Product, fav_in.product_id):
        raise HTTPException(404, "Product not found")

    fav = models.Favorite(user_id=user_id, product_id=fav_in.product_id)
    db.add(fav)
    db.commit()
    db.refresh(fav)
    return fav

def remove_favorite(
    db: Session, user_id: int, product_id: int
) -> None:
    """Delete a favorite or 404 if not found."""
    fav = get_favorite(db, user_id, product_id)
    if not fav:
        raise HTTPException(404, "Favorite not found")
    db.delete(fav)
    db.commit()
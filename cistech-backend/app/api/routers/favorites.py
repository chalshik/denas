from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.firebase_auth import get_current_user
from app.services.auth_service import AuthService
from app.services.favorite_service import (
    get_user_favorites,
    create_favorite,
    remove_favorite,
    get_user_favorite_products  # New function
)
from app.schemas.favorite import FavoriteCreate, FavoriteInDBBase
from app.schemas.product import ProductResponse  # Import for product response

router = APIRouter(
    prefix="/favorites",
    tags=["favorites"]
)

@router.get("/", response_model=List[FavoriteInDBBase])
async def list_favorites(
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user),
):
    """
    List all favorites for the authenticated buyer.
    """
    user = await AuthService.get_user_by_firebase_uid(db, firebase_uid)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return get_user_favorites(db, user.id)

@router.get("/products", response_model=List[ProductResponse])
async def get_favorite_products(
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user),
):
    """
    Get all favorite products for the authenticated buyer.
    Returns full product details for each favorite.
    """
    user = await AuthService.get_user_by_firebase_uid(db, firebase_uid)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return get_user_favorite_products(db, user.id)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=FavoriteInDBBase)
async def add_favorite(
    fav_in: FavoriteCreate,
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user),
):
    """
    Add a product to the authenticated buyer's favorites (idempotent).
    """
    user = await AuthService.get_user_by_firebase_uid(db, firebase_uid)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return create_favorite(db, user.id, fav_in)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_favorite(
    product_id: int,
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user),
):
    """
    Remove a product from the authenticated buyer's favorites.
    """
    user = await AuthService.get_user_by_firebase_uid(db, firebase_uid)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    remove_favorite(db, user.id, product_id)
    return None

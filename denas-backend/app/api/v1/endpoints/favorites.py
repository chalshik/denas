from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.database import get_db
from app.api.dependencies import get_current_user, get_current_user_optional
from app import models, schemas
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=schemas.Favorite, status_code=status.HTTP_201_CREATED)
async def add_favorite(
    favorite_data: schemas.FavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a product to user's favorites"""
    
    # Check if product exists
    product = db.query(models.Product).filter(models.Product.id == favorite_data.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if already favorited
    existing_favorite = db.query(models.Favorite).filter(
        models.Favorite.user_id == current_user.id,
        models.Favorite.product_id == favorite_data.product_id
    ).first()
    
    if existing_favorite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product already in favorites"
        )
    
    # Create favorite
    try:
        db_favorite = models.Favorite(
            user_id=current_user.id,
            product_id=favorite_data.product_id
        )
        db.add(db_favorite)
        db.commit()
        db.refresh(db_favorite)
        return db_favorite
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product already in favorites"
        )


@router.delete("/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    favorite_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a product from user's favorites"""
    
    favorite = db.query(models.Favorite).filter(models.Favorite.id == favorite_id).first()
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found"
        )
    
    # Check if user owns this favorite
    if favorite.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to remove this favorite"
        )
    
    db.delete(favorite)
    db.commit()


@router.delete("/product/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite_by_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a specific product from user's favorites by product_id"""
    
    favorite = db.query(models.Favorite).filter(
        models.Favorite.user_id == current_user.id,
        models.Favorite.product_id == product_id
    ).first()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found"
        )
    
    db.delete(favorite)
    db.commit()


@router.get("/my-favorites", response_model=List[schemas.FavoriteWithProduct])
async def get_my_favorites(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's favorites with product details"""
    
    favorites = db.query(models.Favorite).filter(
        models.Favorite.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    # Add product details to each favorite
    result = []
    for favorite in favorites:
        favorite_dict = {
            "id": favorite.id,
            "user_id": favorite.user_id,
            "product_id": favorite.product_id,
            "created_at": favorite.created_at,
            "product": {
                "id": favorite.product.id,
                "name": favorite.product.name,
                "description": favorite.product.description,
                "price": float(favorite.product.price),
                "stock_quantity": favorite.product.stock_quantity,
                "availability_type": favorite.product.availability_type.value,
                "is_active": favorite.product.is_active,
                "category_id": favorite.product.category_id,
                "created_at": favorite.product.created_at
            }
        }
        result.append(favorite_dict)
    
    return result


# Keep legacy endpoint for backward compatibility
@router.get("/user/{user_id}", response_model=List[schemas.FavoriteWithProduct])
async def get_user_favorites(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get favorites for a specific user (user can only see their own, admins can see any)"""
    
    # Non-admin users can only see their own favorites
    if current_user.role.value not in ["Admin", "Manager"] and user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view other users' favorites"
        )
    
    # Check if user exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    favorites = db.query(models.Favorite).filter(
        models.Favorite.user_id == user_id
    ).offset(skip).limit(limit).all()
    
    # Add product details to each favorite
    result = []
    for favorite in favorites:
        favorite_dict = {
            "id": favorite.id,
            "user_id": favorite.user_id,
            "product_id": favorite.product_id,
            "created_at": favorite.created_at,
            "product": {
                "id": favorite.product.id,
                "name": favorite.product.name,
                "description": favorite.product.description,
                "price": float(favorite.product.price),
                "stock_quantity": favorite.product.stock_quantity,
                "availability_type": favorite.product.availability_type.value,
                "is_active": favorite.product.is_active,
                "category_id": favorite.product.category_id,
                "created_at": favorite.product.created_at
            }
        }
        result.append(favorite_dict)
    
    return result


@router.get("/product/{product_id}/count", response_model=dict)
async def get_product_favorites_count(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get the number of times a product has been favorited (public endpoint)"""
    
    # Check if product exists
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    count = db.query(models.Favorite).filter(models.Favorite.product_id == product_id).count()
    
    return {"product_id": product_id, "favorites_count": count}


@router.get("/product/{product_id}/check", response_model=dict)
async def check_my_favorite(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if current user has favorited a specific product"""
    
    favorite = db.query(models.Favorite).filter(
        models.Favorite.user_id == current_user.id,
        models.Favorite.product_id == product_id
    ).first()
    
    return {
        "user_id": current_user.id,
        "product_id": product_id,
        "is_favorited": favorite is not None,
        "favorite_id": favorite.id if favorite else None
    }


# Keep legacy endpoint for backward compatibility  
@router.get("/user/{user_id}/product/{product_id}/check", response_model=dict)
async def check_user_favorite(
    user_id: int,
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if a user has favorited a specific product (user can only check their own, admins can check any)"""
    
    # Non-admin users can only check their own favorites
    if current_user.role.value not in ["Admin", "Manager"] and user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to check other users' favorites"
        )
    
    favorite = db.query(models.Favorite).filter(
        models.Favorite.user_id == user_id,
        models.Favorite.product_id == product_id
    ).first()
    
    return {
        "user_id": user_id,
        "product_id": product_id,
        "is_favorited": favorite is not None,
        "favorite_id": favorite.id if favorite else None
    } 
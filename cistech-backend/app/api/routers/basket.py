from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.middleware.firebase_auth import get_current_user
from app.schemas.basket import (
    BasketResponse, BasketItemCreate, BasketItemUpdate, BasketItemResponse
)
from app.services.basket_service import BasketService
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/basket",
    tags=["basket"]
)

@router.get("/", response_model=BasketResponse)
async def get_basket(
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user)
):
    print("Fetching basket for user with firebase_uid:", firebase_uid)
    """Get user's basket"""
    user = await AuthService.get_user_by_firebase_uid(db, firebase_uid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    service = BasketService(db)
    basket = service.get_basket(user.id)
    print(f"DEBUG: Basket items count: {len(basket.items)}")
    if basket.items:
        print(f"DEBUG: First item product: {basket.items[0].product}")
        print(f"DEBUG: First item product price: {getattr(basket.items[0].product, 'price', 'NO PRICE')}")
    return basket

@router.post("/items", response_model=BasketItemResponse)
async def add_item_to_basket(
    item: BasketItemCreate,
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user)
):
    """Add item to basket"""
    user = await AuthService.get_user_by_firebase_uid(db, firebase_uid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    service = BasketService(db)
    return service.add_item(user.id, item)

@router.put("/items/{item_id}", response_model=BasketItemResponse)
async def update_basket_item(
    item_id: int,
    item_update: BasketItemUpdate,
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user)
):
    """Update basket item quantity"""
    user = await AuthService.get_user_by_firebase_uid(db, firebase_uid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    service = BasketService(db)
    return service.update_item(user.id, item_id, item_update)

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_basket_item(
    item_id: int,
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user)
):
    """Remove item from basket"""
    user = await AuthService.get_user_by_firebase_uid(db, firebase_uid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    service = BasketService(db)
    service.remove_item(user.id, item_id)

@router.delete("/clear", status_code=status.HTTP_204_NO_CONTENT)
async def clear_basket(
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user)
):
    """Clear all items from basket"""
    user = await AuthService.get_user_by_firebase_uid(db, firebase_uid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    service = BasketService(db)
    service.clear_basket(user.id)

@router.get("/total")
async def get_basket_total(
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user)
):
    """Get basket totals"""
    user = await AuthService.get_user_by_firebase_uid(db, firebase_uid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    service = BasketService(db)
    return service.get_basket_total(user.id)
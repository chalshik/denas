from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
import logging

from app.models.basket import Basket, BasketItem
from app.models.product.product import Product
from app.schemas.basket import BasketItemCreate, BasketItemUpdate
from app import models

logger = logging.getLogger(__name__)

class BasketService:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_basket(self, user_id: int):
        """Get user's basket or create one if it doesn't exist - simplified version"""
        basket = self.db.query(models.Basket).filter(models.Basket.user_id == user_id).first()
        
        if not basket:
            basket = models.Basket(user_id=user_id)
            self.db.add(basket)
            self.db.commit()
            self.db.refresh(basket)
        
        return basket

    def get_basket(self, user_id: int):
        """Get user's basket - simplified version"""
        basket = self.get_or_create_basket(user_id)
        
        # Загружаем items отдельно, чтобы избежать проблем с joinedload
        items = (self.db.query(models.BasketItem)
                .filter(models.BasketItem.basket_id == basket.id)
                .all())
        
        # Загружаем продукты для каждого item
        for item in items:
            if not item.product:
                item.product = self.db.get(models.Product, item.product_id)
        
        basket.items = items
        return basket

    def add_item(self, user_id: int, item_data: BasketItemCreate) -> BasketItem:
        """Add item to basket or update quantity if already exists"""
        # Check if product exists
        product = self.db.query(Product).filter(Product.id == item_data.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Check if product is approved
        if product.status != 'approved':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product is not available for purchase"
            )
        
        # Check if enough quantity available
        if product.quantity < item_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough quantity available. Available: {product.quantity}"
            )
        
        basket = self.get_or_create_basket(user_id)
        
        # Check if item already exists in basket
        existing_item = (self.db.query(BasketItem)
                        .filter(
                            BasketItem.basket_id == basket.id,
                            BasketItem.product_id == item_data.product_id
                        )
                        .first())
        
        if existing_item:
            # Update quantity
            new_quantity = existing_item.quantity + item_data.quantity
            if product.quantity < new_quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Not enough quantity available. Available: {product.quantity}, Requested: {new_quantity}"
                )
            existing_item.quantity = new_quantity
            self.db.commit()
            self.db.refresh(existing_item)
            return existing_item
        else:
            # Create new item
            basket_item = BasketItem(
                basket_id=basket.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity
            )
            self.db.add(basket_item)
            self.db.commit()
            self.db.refresh(basket_item)
            return basket_item

    def update_item(self, user_id: int, item_id: int, item_data: BasketItemUpdate) -> BasketItem:
        """Update basket item quantity"""
        basket = self.get_or_create_basket(user_id)
        
        basket_item = (self.db.query(BasketItem)
                      .filter(
                          BasketItem.id == item_id,
                          BasketItem.basket_id == basket.id
                      )
                      .first())
        
        if not basket_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Basket item not found"
            )
        
        # Check product availability
        product = basket_item.product
        if product.quantity < item_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough quantity available. Available: {product.quantity}"
            )
        
        basket_item.quantity = item_data.quantity
        self.db.commit()
        self.db.refresh(basket_item)
        return basket_item

    def remove_item(self, user_id: int, item_id: int) -> None:
        """Remove item from basket"""
        basket = self.get_or_create_basket(user_id)
        
        basket_item = (self.db.query(BasketItem)
                      .filter(
                          BasketItem.id == item_id,
                          BasketItem.basket_id == basket.id
                      )
                      .first())
        
        if not basket_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Basket item not found"
            )
        
        self.db.delete(basket_item)
        self.db.commit()

    def clear_basket(self, user_id: int) -> None:
        """Clear all items from basket"""
        basket = self.get_or_create_basket(user_id)
        
        self.db.query(BasketItem).filter(BasketItem.basket_id == basket.id).delete()
        self.db.commit()

    def get_basket_total(self, user_id: int) -> dict:
        """Get basket totals"""
        basket = self.get_or_create_basket(user_id)
        
        total_quantity = sum(item.quantity for item in basket.items)
        total_price = sum(float(item.quantity * item.product.price) for item in basket.items)
        
        return {
            "total_quantity": total_quantity,
            "total_price": total_price,
            "items_count": len(basket.items)
        }
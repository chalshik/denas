from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
import logging

from app.db.database import get_db
from app.models.shopping_cart import ShoppingCart as ShoppingCartModel
from app.models.shopping_cart_item import ShoppingCartItem as ShoppingCartItemModel
from app.models.product import Product as ProductModel
from app.schemas.shopping_cart import ShoppingCart, ShoppingCartWithItems
from app.schemas.shopping_cart_item import ShoppingCartItemCreate, ShoppingCartItemUpdate
from app.api.dependencies import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=ShoppingCartWithItems)
async def get_my_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's shopping cart with items
    """
    try:
        cart = db.query(ShoppingCartModel).options(
            joinedload(ShoppingCartModel.cart_items).joinedload(ShoppingCartItemModel.product)
        ).filter(ShoppingCartModel.user_id == current_user.id).first()
        
        # Create cart if doesn't exist
        if not cart:
            cart = ShoppingCartModel(user_id=current_user.id)
            db.add(cart)
            db.commit()
            db.refresh(cart)
        
        return cart
        
    except Exception as e:
        logger.error(f"Error fetching user cart: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch shopping cart"
        )


@router.post("/items", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_item_to_cart(
    item_data: ShoppingCartItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add an item to the shopping cart
    """
    try:
        # Get or create user's cart
        cart = db.query(ShoppingCartModel).filter(ShoppingCartModel.user_id == current_user.id).first()
        if not cart:
            cart = ShoppingCartModel(user_id=current_user.id)
            db.add(cart)
            db.flush()
        
        # Check if product exists
        product = db.query(ProductModel).filter(ProductModel.id == item_data.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        if not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product is not available"
            )
        
        # Check if item already exists in cart
        existing_item = db.query(ShoppingCartItemModel).filter(
            ShoppingCartItemModel.cart_id == cart.id,
            ShoppingCartItemModel.product_id == item_data.product_id
        ).first()
        
        if existing_item:
            # Update quantity if item already exists
            new_quantity = existing_item.quantity + item_data.quantity
            
            # Check stock availability
            if new_quantity > product.stock_quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock. Available: {product.stock_quantity}, Requested: {new_quantity}"
                )
            
            existing_item.quantity = new_quantity
            db.commit()
            
            return {
                "success": True,
                "message": "Item quantity updated in cart",
                "item_id": existing_item.id,
                "new_quantity": new_quantity
            }
        else:
            # Check stock availability
            if item_data.quantity > product.stock_quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock. Available: {product.stock_quantity}, Requested: {item_data.quantity}"
                )
            
            # Create new cart item
            cart_item = ShoppingCartItemModel(
                cart_id=cart.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity
            )
            
            db.add(cart_item)
            db.commit()
            db.refresh(cart_item)
            
            return {
                "success": True,
                "message": "Item added to cart",
                "item_id": cart_item.id,
                "quantity": cart_item.quantity
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding item to cart: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add item to cart"
        )


@router.put("/items/{item_id}", response_model=dict)
async def update_cart_item(
    item_id: int,
    item_data: ShoppingCartItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update cart item quantity
    """
    try:
        # Get cart item and verify ownership
        cart_item = db.query(ShoppingCartItemModel).options(
            joinedload(ShoppingCartItemModel.cart),
            joinedload(ShoppingCartItemModel.product)
        ).filter(ShoppingCartItemModel.id == item_id).first()
        
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found"
            )
        
        if cart_item.cart.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this cart item"
            )
        
        # Check stock availability
        if item_data.quantity > cart_item.product.stock_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock. Available: {cart_item.product.stock_quantity}, Requested: {item_data.quantity}"
            )
        
        old_quantity = cart_item.quantity
        cart_item.quantity = item_data.quantity
        
        db.commit()
        
        return {
            "success": True,
            "message": "Cart item updated",
            "item_id": item_id,
            "old_quantity": old_quantity,
            "new_quantity": item_data.quantity
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating cart item: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update cart item"
        )


@router.delete("/items/{item_id}")
async def remove_cart_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove an item from the shopping cart
    """
    try:
        # Get cart item and verify ownership
        cart_item = db.query(ShoppingCartItemModel).options(
            joinedload(ShoppingCartItemModel.cart)
        ).filter(ShoppingCartItemModel.id == item_id).first()
        
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found"
            )
        
        if cart_item.cart.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to remove this cart item"
            )
        
        db.delete(cart_item)
        db.commit()
        
        return {"success": True, "message": "Item removed from cart"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing cart item: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove cart item"
        )


@router.delete("/clear")
async def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Clear all items from the shopping cart
    """
    try:
        # Get user's cart
        cart = db.query(ShoppingCartModel).filter(ShoppingCartModel.user_id == current_user.id).first()
        
        if not cart:
            return {"success": True, "message": "Cart is already empty"}
        
        # Delete all cart items
        db.query(ShoppingCartItemModel).filter(ShoppingCartItemModel.cart_id == cart.id).delete()
        db.commit()
        
        return {"success": True, "message": "Cart cleared successfully"}
        
    except Exception as e:
        logger.error(f"Error clearing cart: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear cart"
        )


@router.get("/summary", response_model=dict)
async def get_cart_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get cart summary with total items and total price
    """
    try:
        cart = db.query(ShoppingCartModel).options(
            joinedload(ShoppingCartModel.cart_items).joinedload(ShoppingCartItemModel.product)
        ).filter(ShoppingCartModel.user_id == current_user.id).first()
        
        if not cart:
            return {
                "total_items": 0,
                "total_price": 0.0,
                "items_count": 0
            }
        
        total_items = sum(item.quantity for item in cart.cart_items)
        total_price = sum(item.quantity * item.product.price for item in cart.cart_items)
        items_count = len(cart.cart_items)
        
        return {
            "total_items": total_items,
            "total_price": float(total_price),
            "items_count": items_count
        }
        
    except Exception as e:
        logger.error(f"Error getting cart summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get cart summary"
        ) 
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.db.database import get_db
from app.services.shopping_cart_service import ShoppingCartService
from app.schemas.shopping_cart import (
    ShoppingCartResponse, 
    ShoppingCartSummary,
    CartActionResponse,
    CartClearResponse
)
from app.schemas.shopping_cart_item import (
    ShoppingCartItemCreate, 
    ShoppingCartItemUpdate,
    ShoppingCartItemWithProduct
)
from app.api.dependencies import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=ShoppingCartResponse)
async def get_my_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's shopping cart with all items and product details
    """
    try:
        service = ShoppingCartService(db)
        cart = service.get_cart_with_items(current_user.id)
        
        if not cart:
            # Create an empty cart for the user
            cart = service.get_or_create_user_cart(current_user.id)
            # Commit the cart creation and refresh to get the created_at timestamp
            service.db.commit()
            service.db.refresh(cart)
        
        return cart
        
    except Exception as e:
        logger.error(f"Error fetching user cart: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch shopping cart"
        )


@router.post("/items", response_model=CartActionResponse, status_code=status.HTTP_201_CREATED)
async def add_item_to_cart(
    item_data: ShoppingCartItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add an item to the shopping cart
    """
    try:
        service = ShoppingCartService(db)
        result = service.add_item_to_cart(
            user_id=current_user.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity
        )
        return CartActionResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error adding item to cart: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add item to cart"
        )


@router.put("/items/{item_id}", response_model=CartActionResponse)
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
        service = ShoppingCartService(db)
        result = service.update_cart_item(
            user_id=current_user.id,
            item_id=item_id,
            quantity=item_data.quantity
        )
        return CartActionResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating cart item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update cart item"
        )


@router.get("/items/{item_id}", response_model=ShoppingCartItemWithProduct)
async def get_cart_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific cart item with full product details
    """
    try:
        service = ShoppingCartService(db)
        cart_item = service.get_cart_item_with_details(current_user.id, item_id)
        
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found"
            )
        
        return cart_item
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching cart item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch cart item"
        )


@router.delete("/items/{item_id}", response_model=CartActionResponse)
async def remove_cart_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove an item from the shopping cart
    """
    try:
        service = ShoppingCartService(db)
        result = service.remove_cart_item(current_user.id, item_id)
        return CartActionResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error removing cart item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove cart item"
        )


@router.delete("/clear", response_model=CartClearResponse)
async def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Clear all items from the shopping cart
    """
    try:
        service = ShoppingCartService(db)
        result = service.clear_cart(current_user.id)
        return CartClearResponse(**result)
        
    except Exception as e:
        logger.error(f"Error clearing cart: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear cart"
        )


@router.get("/summary", response_model=ShoppingCartSummary)
async def get_cart_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get cart summary with total items and total price
    """
    try:
        service = ShoppingCartService(db)
        result = service.get_cart_summary(current_user.id)
        return ShoppingCartSummary(**result)
        
    except Exception as e:
        logger.error(f"Error getting cart summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get cart summary"
        ) 
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func
from typing import Optional, Dict, Any
import logging

from app.models.shopping_cart import ShoppingCart as ShoppingCartModel
from app.models.shopping_cart_item import ShoppingCartItem as ShoppingCartItemModel
from app.models.product import Product as ProductModel
from app.models.user import User

logger = logging.getLogger(__name__)


class ShoppingCartValidator:
    """Validation logic for shopping cart operations"""
    
    @staticmethod
    def validate_product_availability(product: ProductModel, requested_quantity: int) -> None:
        """Validate if product is available and has sufficient stock"""
        if not product:
            raise ValueError("Product not found")
        
        if not product.is_active:
            raise ValueError("Product is not available")
        
        if requested_quantity > product.stock_quantity:
            raise ValueError(
                f"Insufficient stock. Available: {product.stock_quantity}, "
                f"Requested: {requested_quantity}"
            )
    
    @staticmethod
    def validate_cart_item_ownership(cart_item: ShoppingCartItemModel, user_id: int) -> None:
        """Validate if user owns the cart item"""
        if not cart_item:
            raise ValueError("Cart item not found")
        
        if cart_item.cart.user_id != user_id:
            raise ValueError("Not authorized to access this cart item")


class ShoppingCartService:
    """Service layer for shopping cart operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.validator = ShoppingCartValidator()
    
    def get_or_create_user_cart(self, user_id: int) -> ShoppingCartModel:
        """Get existing cart or create new one for user"""
        try:
            cart = self.db.query(ShoppingCartModel).filter(
                ShoppingCartModel.user_id == user_id
            ).first()
            
            if not cart:
                cart = ShoppingCartModel(user_id=user_id)
                self.db.add(cart)
                self.db.flush()  # Get the ID without committing
            
            return cart
            
        except Exception as e:
            logger.error(f"Error getting/creating cart for user {user_id}: {str(e)}")
            self.db.rollback()
            raise
    
    def get_cart_with_items(self, user_id: int) -> Optional[ShoppingCartModel]:
        """Get user's cart with all items and product details"""
        try:
            cart = self.db.query(ShoppingCartModel).options(
                selectinload(ShoppingCartModel.cart_items).options(
                    joinedload(ShoppingCartItemModel.product).options(
                        joinedload(ProductModel.category),
                        selectinload(ProductModel.images)
                    )
                )
            ).filter(ShoppingCartModel.user_id == user_id).first()
            
            return cart
            
        except Exception as e:
            logger.error(f"Error fetching cart for user {user_id}: {str(e)}")
            raise
    
    def add_item_to_cart(self, user_id: int, product_id: int, quantity: int) -> Dict[str, Any]:
        """Add item to cart or update quantity if exists"""
        try:
            # Get or create cart
            cart = self.get_or_create_user_cart(user_id)
            
            # Get product with category and images
            product = self.db.query(ProductModel).options(
                joinedload(ProductModel.category),
                selectinload(ProductModel.images)
            ).filter(ProductModel.id == product_id).first()
            
            # Check existing cart item
            existing_item = self.db.query(ShoppingCartItemModel).filter(
                ShoppingCartItemModel.cart_id == cart.id,
                ShoppingCartItemModel.product_id == product_id
            ).first()
            
            if existing_item:
                new_quantity = existing_item.quantity + quantity
                self.validator.validate_product_availability(product, new_quantity)
                
                existing_item.quantity = new_quantity
                self.db.commit()
                
                return {
                    "success": True,
                    "message": "Item quantity updated in cart",
                    "item_id": existing_item.id,
                    "new_quantity": new_quantity,
                    "action": "updated"
                }
            else:
                self.validator.validate_product_availability(product, quantity)
                
                cart_item = ShoppingCartItemModel(
                    cart_id=cart.id,
                    product_id=product_id,
                    quantity=quantity
                )
                
                self.db.add(cart_item)
                self.db.commit()
                self.db.refresh(cart_item)
                
                return {
                    "success": True,
                    "message": "Item added to cart",
                    "item_id": cart_item.id,
                    "quantity": cart_item.quantity,
                    "action": "added"
                }
                
        except ValueError as e:
            self.db.rollback()
            raise ValueError(str(e))
        except Exception as e:
            logger.error(f"Error adding item to cart: {str(e)}")
            self.db.rollback()
            raise
    
    def update_cart_item(self, user_id: int, item_id: int, quantity: int) -> Dict[str, Any]:
        """Update cart item quantity"""
        try:
            # Get cart item with product and cart details
            cart_item = self.db.query(ShoppingCartItemModel).options(
                joinedload(ShoppingCartItemModel.cart),
                joinedload(ShoppingCartItemModel.product)
            ).filter(ShoppingCartItemModel.id == item_id).first()
            
            self.validator.validate_cart_item_ownership(cart_item, user_id)
            self.validator.validate_product_availability(cart_item.product, quantity)
            
            old_quantity = cart_item.quantity
            cart_item.quantity = quantity
            
            self.db.commit()
            
            return {
                "success": True,
                "message": "Cart item updated",
                "item_id": item_id,
                "old_quantity": old_quantity,
                "new_quantity": quantity
            }
            
        except ValueError as e:
            self.db.rollback()
            raise ValueError(str(e))
        except Exception as e:
            logger.error(f"Error updating cart item {item_id}: {str(e)}")
            self.db.rollback()
            raise
    
    def remove_cart_item(self, user_id: int, item_id: int) -> Dict[str, Any]:
        """Remove item from cart"""
        try:
            cart_item = self.db.query(ShoppingCartItemModel).options(
                joinedload(ShoppingCartItemModel.cart),
                joinedload(ShoppingCartItemModel.product)
            ).filter(ShoppingCartItemModel.id == item_id).first()
            
            self.validator.validate_cart_item_ownership(cart_item, user_id)
            
            product_name = cart_item.product.name
            self.db.delete(cart_item)
            self.db.commit()
            
            return {
                "success": True,
                "message": f"'{product_name}' removed from cart",
                "item_id": item_id
            }
            
        except ValueError as e:
            self.db.rollback()
            raise ValueError(str(e))
        except Exception as e:
            logger.error(f"Error removing cart item {item_id}: {str(e)}")
            self.db.rollback()
            raise
    
    def clear_cart(self, user_id: int) -> Dict[str, Any]:
        """Clear all items from user's cart"""
        try:
            cart = self.db.query(ShoppingCartModel).filter(
                ShoppingCartModel.user_id == user_id
            ).first()
            
            if not cart:
                return {
                    "success": True,
                    "message": "Cart is already empty",
                    "items_removed": 0
                }
            
            # Count items before deletion
            items_count = self.db.query(ShoppingCartItemModel).filter(
                ShoppingCartItemModel.cart_id == cart.id
            ).count()
            
            # Delete all cart items
            self.db.query(ShoppingCartItemModel).filter(
                ShoppingCartItemModel.cart_id == cart.id
            ).delete()
            
            self.db.commit()
            
            return {
                "success": True,
                "message": "Cart cleared successfully",
                "items_removed": items_count
            }
            
        except Exception as e:
            logger.error(f"Error clearing cart for user {user_id}: {str(e)}")
            self.db.rollback()
            raise
    
    def get_cart_summary(self, user_id: int) -> Dict[str, Any]:
        """Get cart summary with totals"""
        try:
            cart = self.get_cart_with_items(user_id)
            
            if not cart or not cart.cart_items:
                return {
                    "total_items": 0,
                    "total_price": 0.0,
                    "items_count": 0,
                    "cart_id": None
                }
            
            total_items = sum(item.quantity for item in cart.cart_items)
            total_price = sum(item.quantity * item.product.price for item in cart.cart_items)
            items_count = len(cart.cart_items)
            
            return {
                "total_items": total_items,
                "total_price": float(total_price),
                "items_count": items_count,
                "cart_id": cart.id
            }
            
        except Exception as e:
            logger.error(f"Error getting cart summary for user {user_id}: {str(e)}")
            raise
    
    def get_cart_item_with_details(self, user_id: int, item_id: int) -> Optional[ShoppingCartItemModel]:
        """Get specific cart item with full product details"""
        try:
            cart_item = self.db.query(ShoppingCartItemModel).options(
                joinedload(ShoppingCartItemModel.cart),
                joinedload(ShoppingCartItemModel.product).options(
                    joinedload(ProductModel.category),
                    selectinload(ProductModel.images)
                )
            ).filter(
                ShoppingCartItemModel.id == item_id,
                ShoppingCartItemModel.cart.has(ShoppingCartModel.user_id == user_id)
            ).first()
            
            return cart_item
            
        except Exception as e:
            logger.error(f"Error fetching cart item {item_id} for user {user_id}: {str(e)}")
            raise 
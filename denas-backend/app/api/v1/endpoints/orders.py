from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import logging
from decimal import Decimal

from app.db.database import get_db
from app.models.order import Order as OrderModel, OrderStatus
from app.models.order_item import OrderItem as OrderItemModel
from app.models.product import Product as ProductModel
from app.schemas.order import Order, OrderCreate, OrderUpdate, OrderWithItems
from app.api.dependencies import get_current_user, require_admin_access
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()

# User endpoints
@router.get("/my-orders", response_model=List[OrderWithItems])
async def get_my_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[OrderStatus] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's orders with items
    """
    try:
        query = db.query(OrderModel).options(
            joinedload(OrderModel.order_items).joinedload(OrderItemModel.product)
        ).filter(OrderModel.user_id == current_user.id)
        
        if status_filter:
            query = query.filter(OrderModel.status == status_filter)
        
        orders = query.order_by(OrderModel.created_at.desc()).offset(skip).limit(limit).all()
        return orders
        
    except Exception as e:
        logger.error(f"Error fetching user orders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch orders"
        )


@router.get("/{order_id}", response_model=OrderWithItems)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific order (user can only see their own orders, admins can see all)
    """
    try:
        query = db.query(OrderModel).options(
            joinedload(OrderModel.order_items).joinedload(OrderItemModel.product),
            joinedload(OrderModel.user)
        ).filter(OrderModel.id == order_id)
        
        # Non-admin users can only see their own orders
        if current_user.role.value not in ["Admin", "Manager"]:
            query = query.filter(OrderModel.user_id == current_user.id)
        
        order = query.first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        return order
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching order {order_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch order"
        )


@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new order with items
    """
    try:
        # Calculate total price from order items
        total_price = Decimal('0.00')
        
        # Validate all products exist and calculate total
        for item in order_data.order_items:
            product = db.query(ProductModel).filter(ProductModel.id == item.product_id).first()
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product with ID {item.product_id} not found"
                )
            
            if not product.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product '{product.name}' is not available"
                )
            
            if product.stock_quantity < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for product '{product.name}'. Available: {product.stock_quantity}, Requested: {item.quantity}"
                )
            
            total_price += product.price * item.quantity
        
        # Create order
        order = OrderModel(
            user_id=current_user.id,
            status=OrderStatus.PENDING,
            total_price=total_price
        )
        
        db.add(order)
        db.flush()  # Get order ID
        
        # Create order items
        for item_data in order_data.order_items:
            product = db.query(ProductModel).filter(ProductModel.id == item_data.product_id).first()
            
            order_item = OrderItemModel(
                order_id=order.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                price=product.price  # Store current price
            )
            db.add(order_item)
            
            # Update product stock
            product.stock_quantity -= item_data.quantity
        
        db.commit()
        db.refresh(order)
        
        logger.info(f"Order created successfully: ID {order.id} for user {current_user.id}")
        return order
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create order"
        )


@router.put("/{order_id}/status", response_model=Order)
async def update_order_status(
    order_id: int,
    new_status: OrderStatus,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update order status (users can cancel their own pending orders, admins can update any order)
    """
    try:
        order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Check permissions
        is_admin = current_user.role.value in ["Admin", "Manager"]
        is_owner = order.user_id == current_user.id
        
        if not is_admin and not is_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this order"
            )
        
        # Users can only cancel their own pending orders
        if not is_admin and (new_status != OrderStatus.CANCELLED or order.status != OrderStatus.PENDING):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only cancel your own pending orders"
            )
        
        # Handle stock restoration for cancelled orders
        if new_status == OrderStatus.CANCELLED and order.status != OrderStatus.CANCELLED:
            # Restore product stock
            order_items = db.query(OrderItemModel).filter(OrderItemModel.order_id == order_id).all()
            for item in order_items:
                product = db.query(ProductModel).filter(ProductModel.id == item.product_id).first()
                if product:
                    product.stock_quantity += item.quantity
        
        old_status = order.status
        order.status = new_status
        
        db.commit()
        db.refresh(order)
        
        logger.info(f"Order {order_id} status updated from {old_status} to {new_status} by user {current_user.id}")
        return order
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating order status: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update order status"
        )


# Admin endpoints
@router.get("/", response_model=List[OrderWithItems])
async def get_all_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[OrderStatus] = Query(None),
    user_id: Optional[int] = Query(None),
    admin_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """
    Get all orders with filtering (admin only)
    """
    try:
        query = db.query(OrderModel).options(
            joinedload(OrderModel.order_items).joinedload(OrderItemModel.product),
            joinedload(OrderModel.user)
        )
        
        if status_filter:
            query = query.filter(OrderModel.status == status_filter)
        if user_id:
            query = query.filter(OrderModel.user_id == user_id)
        
        orders = query.order_by(OrderModel.created_at.desc()).offset(skip).limit(limit).all()
        return orders
        
    except Exception as e:
        logger.error(f"Error fetching all orders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch orders"
        )


@router.get("/stats/summary", response_model=dict)
async def get_order_stats(
    admin_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """
    Get order statistics (admin only)
    """
    try:
        total_orders = db.query(OrderModel).count()
        pending_orders = db.query(OrderModel).filter(OrderModel.status == OrderStatus.PENDING).count()
        completed_orders = db.query(OrderModel).filter(OrderModel.status == OrderStatus.COMPLETED).count()
        cancelled_orders = db.query(OrderModel).filter(OrderModel.status == OrderStatus.CANCELLED).count()
        
        # Calculate total revenue from completed orders
        total_revenue_result = db.query(OrderModel.total_price).filter(
            OrderModel.status == OrderStatus.COMPLETED
        ).all()
        total_revenue = sum(order.total_price for order in total_revenue_result) if total_revenue_result else 0
        
        return {
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "completed_orders": completed_orders,
            "cancelled_orders": cancelled_orders,
            "total_revenue": float(total_revenue)
        }
        
    except Exception as e:
        logger.error(f"Error fetching order stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch order statistics"
        )


@router.delete("/{order_id}")
async def delete_order(
    order_id: int,
    admin_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """
    Delete an order (admin only) - only for cancelled orders
    """
    try:
        order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        if order.status != OrderStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only cancelled orders can be deleted"
            )
        
        # Delete order items first (due to foreign key constraints)
        db.query(OrderItemModel).filter(OrderItemModel.order_id == order_id).delete()
        
        # Delete order
        db.delete(order)
        db.commit()
        
        logger.info(f"Order deleted successfully: ID {order_id} by admin {admin_user.id}")
        return {"success": True, "message": "Order deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting order {order_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete order"
        ) 
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import logging

from app.db.database import get_db
from app.models.payment import Payment as PaymentModel, PaymentStatus
from app.models.order import Order as OrderModel, OrderStatus
from app.schemas.payment import Payment, PaymentCreate, PaymentUpdate, PaymentWithOrder
from app.api.dependencies import get_current_user, require_admin_access
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()

# User endpoints
@router.get("/my-payments", response_model=List[PaymentWithOrder])
async def get_my_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[PaymentStatus] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's payments with order details
    """
    try:
        # Get payments for user's orders
        query = db.query(PaymentModel).options(
            joinedload(PaymentModel.order).joinedload(OrderModel.user)
        ).join(OrderModel).filter(OrderModel.user_id == current_user.id)
        
        if status_filter:
            query = query.filter(PaymentModel.status == status_filter)
        
        payments = query.order_by(PaymentModel.created_at.desc()).offset(skip).limit(limit).all()
        return payments
        
    except Exception as e:
        logger.error(f"Error fetching user payments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch payments"
        )


@router.get("/{payment_id}", response_model=PaymentWithOrder)
async def get_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific payment (user can only see their own payments, admins can see all)
    """
    try:
        query = db.query(PaymentModel).options(
            joinedload(PaymentModel.order).joinedload(OrderModel.user)
        ).filter(PaymentModel.id == payment_id)
        
        payment = query.first()
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        # Non-admin users can only see their own payments
        if current_user.role.value not in ["Admin", "Manager"] and payment.order.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this payment"
            )
        
        return payment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching payment {payment_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch payment"
        )


@router.post("/", response_model=Payment, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new payment for an order
    """
    try:
        # Verify order exists and belongs to user (unless admin)
        order = db.query(OrderModel).filter(OrderModel.id == payment_data.order_id).first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Non-admin users can only create payments for their own orders
        if current_user.role.value not in ["Admin", "Manager"] and order.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create payment for this order"
            )
        
        # Check if order is in valid state for payment
        if order.status not in [OrderStatus.PENDING, OrderStatus.PAID]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order is not in a valid state for payment"
            )
        
        # Validate payment amount matches order total
        if payment_data.amount != order.total_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payment amount ({payment_data.amount}) must match order total ({order.total_price})"
            )
        
        # Create payment
        payment = PaymentModel(**payment_data.dict())
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        logger.info(f"Payment created successfully: ID {payment.id} for order {order.id} by user {current_user.id}")
        return payment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating payment: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create payment"
        )


@router.put("/{payment_id}/status", response_model=Payment)
async def update_payment_status(
    payment_id: int,
    new_status: PaymentStatus,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update payment status (admins only, or users for their own pending payments to failed)
    """
    try:
        payment = db.query(PaymentModel).options(
            joinedload(PaymentModel.order)
        ).filter(PaymentModel.id == payment_id).first()
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        # Check permissions
        is_admin = current_user.role.value in ["Admin", "Manager"]
        is_owner = payment.order.user_id == current_user.id
        
        if not is_admin and not is_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this payment"
            )
        
        # Users can only mark their own pending payments as failed
        if not is_admin and (new_status != PaymentStatus.FAILED or payment.status != PaymentStatus.PENDING):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only mark your own pending payments as failed"
            )
        
        old_status = payment.status
        payment.status = new_status
        
        # Update order status based on payment status
        if new_status == PaymentStatus.COMPLETED and payment.order.status == OrderStatus.PENDING:
            payment.order.status = OrderStatus.PAID
        elif new_status == PaymentStatus.FAILED and payment.order.status == OrderStatus.PAID:
            payment.order.status = OrderStatus.PENDING
        
        db.commit()
        db.refresh(payment)
        
        logger.info(f"Payment {payment_id} status updated from {old_status} to {new_status} by user {current_user.id}")
        return payment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating payment status: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update payment status"
        )


# Admin endpoints
@router.get("/", response_model=List[PaymentWithOrder])
async def get_all_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[PaymentStatus] = Query(None),
    provider_filter: Optional[str] = Query(None),
    order_id: Optional[int] = Query(None),
    admin_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """
    Get all payments with filtering (admin only)
    """
    try:
        query = db.query(PaymentModel).options(
            joinedload(PaymentModel.order).joinedload(OrderModel.user)
        )
        
        if status_filter:
            query = query.filter(PaymentModel.status == status_filter)
        if provider_filter:
            query = query.filter(PaymentModel.payment_provider.ilike(f"%{provider_filter}%"))
        if order_id:
            query = query.filter(PaymentModel.order_id == order_id)
        
        payments = query.order_by(PaymentModel.created_at.desc()).offset(skip).limit(limit).all()
        return payments
        
    except Exception as e:
        logger.error(f"Error fetching all payments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch payments"
        )


@router.get("/stats/summary", response_model=dict)
async def get_payment_stats(
    admin_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """
    Get payment statistics (admin only)
    """
    try:
        total_payments = db.query(PaymentModel).count()
        pending_payments = db.query(PaymentModel).filter(PaymentModel.status == PaymentStatus.PENDING).count()
        completed_payments = db.query(PaymentModel).filter(PaymentModel.status == PaymentStatus.COMPLETED).count()
        failed_payments = db.query(PaymentModel).filter(PaymentModel.status == PaymentStatus.FAILED).count()
        
        # Calculate total processed amount (completed payments)
        completed_amount_result = db.query(PaymentModel.amount).filter(
            PaymentModel.status == PaymentStatus.COMPLETED
        ).all()
        total_processed = sum(payment.amount for payment in completed_amount_result) if completed_amount_result else 0
        
        # Calculate pending amount
        pending_amount_result = db.query(PaymentModel.amount).filter(
            PaymentModel.status == PaymentStatus.PENDING
        ).all()
        total_pending = sum(payment.amount for payment in pending_amount_result) if pending_amount_result else 0
        
        return {
            "total_payments": total_payments,
            "pending_payments": pending_payments,
            "completed_payments": completed_payments,
            "failed_payments": failed_payments,
            "total_processed_amount": float(total_processed),
            "total_pending_amount": float(total_pending)
        }
        
    except Exception as e:
        logger.error(f"Error fetching payment stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch payment statistics"
        )


@router.delete("/{payment_id}")
async def delete_payment(
    payment_id: int,
    admin_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """
    Delete a payment (admin only) - only for failed payments
    """
    try:
        payment = db.query(PaymentModel).filter(PaymentModel.id == payment_id).first()
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        if payment.status != PaymentStatus.FAILED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only failed payments can be deleted"
            )
        
        db.delete(payment)
        db.commit()
        
        logger.info(f"Payment deleted successfully: ID {payment_id} by admin {admin_user.id}")
        return {"success": True, "message": "Payment deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting payment {payment_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete payment"
        ) 
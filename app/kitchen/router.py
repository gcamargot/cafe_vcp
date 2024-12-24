from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import and_, or_

from ..database import get_db
from ..models import Order, OrderItem, Product
from ..orders.schemas import Order as OrderSchema, OrderStatus
from ..auth.middleware import check_permissions

router = APIRouter(
    prefix="/kitchen",
    tags=["kitchen"]
)

@router.get("/orders/queue", response_model=List[OrderSchema])
async def get_kitchen_queue(
    db: Session = Depends(get_db),
    _=Depends(check_permissions(["cook"]))
):
    """Obtener la cola de órdenes pendientes y en preparación, ordenadas por tiempo de espera."""
    orders = db.query(Order).filter(
        Order.status.in_([OrderStatus.PENDING, OrderStatus.IN_PREPARATION])
    ).order_by(Order.created_at.asc()).all()
    return orders

@router.get("/orders/next", response_model=OrderSchema)
async def get_next_order(
    db: Session = Depends(get_db),
    _=Depends(check_permissions(["cook"]))
):
    """Obtener la siguiente orden pendiente más antigua."""
    order = db.query(Order).filter(
        Order.status == OrderStatus.PENDING
    ).order_by(Order.created_at.asc()).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay órdenes pendientes"
        )
    return order

@router.post("/orders/{order_id}/start", response_model=OrderSchema)
async def start_order_preparation(
    order_id: int,
    db: Session = Depends(get_db),
    _=Depends(check_permissions(["cook"]))
):
    """Marcar una orden como 'en preparación'."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden no encontrada"
        )

    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La orden no está en estado pendiente"
        )

    order.status = OrderStatus.IN_PREPARATION
    db.commit()
    db.refresh(order)
    return order

@router.post("/orders/{order_id}/complete", response_model=OrderSchema)
async def complete_order(
    order_id: int,
    db: Session = Depends(get_db),
    _=Depends(check_permissions(["cook"]))
):
    """Marcar una orden como 'lista'."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden no encontrada"
        )

    if order.status != OrderStatus.IN_PREPARATION:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La orden no está en preparación"
        )

    order.status = OrderStatus.READY
    db.commit()
    db.refresh(order)
    return order

@router.get("/orders/stats")
async def get_kitchen_stats(
    db: Session = Depends(get_db),
    _=Depends(check_permissions(["cook", "admin"]))
):
    """Obtener estadísticas de la cocina."""
    current_time = datetime.utcnow()
    today_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)

    # Órdenes del día
    total_orders = db.query(Order).filter(
        Order.created_at >= today_start
    ).count()

    pending_orders = db.query(Order).filter(
        and_(
            Order.status == OrderStatus.PENDING,
            Order.created_at >= today_start
        )
    ).count()

    in_preparation = db.query(Order).filter(
        and_(
            Order.status == OrderStatus.IN_PREPARATION,
            Order.created_at >= today_start
        )
    ).count()

    completed_orders = db.query(Order).filter(
        and_(
            Order.status == OrderStatus.READY,
            Order.created_at >= today_start
        )
    ).count()

    # Calcular tiempo promedio de preparación
    completed_orders_data = db.query(Order).filter(
        and_(
            Order.status == OrderStatus.READY,
            Order.created_at >= today_start
        )
    ).all()

    if completed_orders_data:
        avg_preparation_time = sum(
            (order.updated_at - order.created_at).total_seconds()
            for order in completed_orders_data
        ) / len(completed_orders_data)
    else:
        avg_preparation_time = 0

    return {
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "in_preparation": in_preparation,
        "completed_orders": completed_orders,
        "avg_preparation_time": round(avg_preparation_time / 60, 2),  # en minutos
    }

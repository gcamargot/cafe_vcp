from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import and_

from ..database import get_db
from ..models import Order, OrderItem, Product, Table
from .schemas import OrderCreate, Order as OrderSchema, OrderUpdate, OrderStatus
from ..auth.middleware import check_permissions
from ..auth.router import get_current_user

router = APIRouter(
    prefix="/orders",
    tags=["orders"]
)

@router.post("/", response_model=OrderSchema, status_code=status.HTTP_201_CREATED)
async def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Crear una nueva orden."""
    # Verificar que la mesa existe y está disponible
    table = db.query(Table).filter(Table.id == order.table_id).first()
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mesa no encontrada"
        )
    if table.status != "free":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mesa no disponible"
        )

    # Verificar que todos los productos existen y tienen stock
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto {item.product_id} no encontrado"
            )
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuficiente para el producto {product.name}"
            )

    # Crear la orden
    db_order = Order(
        table_id=order.table_id,
        user_id=current_user.id,
        status=OrderStatus.PENDING,
        notes=order.notes
    )
    db.add(db_order)
    db.flush()  # Para obtener el ID de la orden

    # Crear los items y actualizar stock
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        order_item = OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=product.price,
            notes=item.notes
        )
        db.add(order_item)
        product.stock -= item.quantity

    # Actualizar estado de la mesa
    table.status = "occupied"

    try:
        db.commit()
        db.refresh(db_order)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    return db_order

@router.get("/", response_model=List[OrderSchema])
async def get_orders(
    status: Optional[OrderStatus] = Query(None, description="Filtrar por estado"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(check_permissions(["admin", "cashier", "cook"]))
):
    """Obtener todas las órdenes con filtros opcionales."""
    query = db.query(Order)

    if status:
        query = query.filter(Order.status == status)

    orders = query.offset(skip).limit(limit).all()
    return orders

@router.get("/{order_id}", response_model=OrderSchema)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    _=Depends(check_permissions(["admin", "cashier", "cook"]))
):
    """Obtener una orden específica."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden no encontrada"
        )
    return order

@router.patch("/{order_id}", response_model=OrderSchema)
async def update_order_status(
    order_id: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db),
    _=Depends(check_permissions(["admin", "cashier", "cook"]))
):
    """Actualizar el estado de una orden."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden no encontrada"
        )

    if order_update.status:
        order.status = order_update.status

    if order_update.notes is not None:
        order.notes = order_update.notes

    try:
        db.commit()
        db.refresh(order)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    return order

@router.get("/kitchen/pending", response_model=List[OrderSchema])
async def get_kitchen_orders(
    db: Session = Depends(get_db),
    _=Depends(check_permissions(["cook"]))
):
    """Obtener órdenes pendientes para la cocina."""
    orders = db.query(Order).filter(
        Order.status.in_([OrderStatus.PENDING, OrderStatus.IN_PREPARATION])
    ).all()
    return orders

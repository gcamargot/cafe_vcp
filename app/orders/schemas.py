from pydantic import BaseModel, condecimal
from typing import List, Optional
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = 'pending'
    IN_PREPARATION = 'in_preparation'
    READY = 'ready'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'

class PaymentStatus(str, Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    notes: Optional[str] = None

class OrderItem(OrderItemCreate):
    id: int
    unit_price: condecimal(decimal_places=2)
    created_at: datetime

    class Config:
        orm_mode = True

class OrderCreate(BaseModel):
    table_id: int
    items: List[OrderItemCreate]
    notes: Optional[str] = None

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    notes: Optional[str] = None

class Order(BaseModel):
    id: int
    table_id: int
    user_id: int
    status: OrderStatus
    total_amount: condecimal(decimal_places=2)
    payment_status: PaymentStatus
    notes: Optional[str]
    created_at: datetime
    items: List[OrderItem]

    class Config:
        orm_mode = True

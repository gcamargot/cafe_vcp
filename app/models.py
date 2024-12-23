from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum, DECIMAL
from sqlalchemy.orm import relationship
import enum
from .database import Base

class TableStatus(str, enum.Enum):
    FREE = 'free'
    OCCUPIED = 'occupied'
    PENDING_PAYMENT = 'pending_payment'

class OrderStatus(str, enum.Enum):
    PENDING = 'pending'
    IN_PREPARATION = 'in_preparation'
    READY = 'ready'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'

class PaymentStatus(str, enum.Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'

class PaymentMethod(str, enum.Enum):
    CASH = 'cash'
    MERCADOPAGO = 'mercadopago'
    CRYPTO = 'crypto'

class UserRole(str, enum.Enum):
    CASHIER = 'cashier'
    COOK = 'cook'
    ADMIN = 'admin'

# Definiciones de ENUM como strings para PostgreSQL
table_status = Enum(TableStatus)
order_status = Enum(OrderStatus)
payment_status = Enum(PaymentStatus)
payment_method = Enum(PaymentMethod)
user_role = Enum(UserRole)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(user_role, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)

    orders = relationship("Order", back_populates="user")

class Table(Base):
    __tablename__ = 'tables'

    id = Column(Integer, primary_key=True)
    status = Column(table_status, default=TableStatus.FREE)
    capacity = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    orders = relationship("Order", back_populates="table")

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    category = Column(String(50), nullable=False)
    stock = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order_items = relationship("OrderItem", back_populates="product")

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    table_id = Column(Integer, ForeignKey('tables.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(order_status, default=OrderStatus.PENDING)
    total_amount = Column(DECIMAL(10, 2), default=0)
    payment_status = Column(payment_status, default=PaymentStatus.PENDING)
    notes = Column(Text)

    table = relationship("Table", back_populates="orders")
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order")

class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

class Payment(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    method = Column(payment_method, nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    status = Column(payment_status, default=PaymentStatus.PENDING)
    external_ref = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="payments")

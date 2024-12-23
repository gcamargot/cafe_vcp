from pydantic import BaseModel, conint
from datetime import datetime
from typing import Optional
from enum import Enum

class TableStatus(str, Enum):
    FREE = 'free'
    OCCUPIED = 'occupied'
    PENDING_PAYMENT = 'pending_payment'

class TableBase(BaseModel):
    capacity: conint(gt=0)  # Debe ser mayor que 0

class TableCreate(TableBase):
    pass

class TableUpdate(TableBase):
    capacity: Optional[conint(gt=0)] = None
    status: Optional[TableStatus] = None
    is_active: Optional[bool] = None

class Table(TableBase):
    id: int
    status: TableStatus
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

class TableStatusUpdate(BaseModel):
    status: TableStatus

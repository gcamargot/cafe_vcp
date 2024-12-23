from pydantic import BaseModel, condecimal, conint
from typing import Optional
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    price: condecimal(gt=0, decimal_places=2)  # Mayor que 0, 2 decimales
    category: str
    description: Optional[str] = None
    stock: conint(ge=0) = 0  # Mayor o igual a 0

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[condecimal(gt=0, decimal_places=2)] = None
    category: Optional[str] = None
    description: Optional[str] = None
    stock: Optional[conint(ge=0)] = None
    is_active: Optional[bool] = None

class Product(ProductBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ProductStockUpdate(BaseModel):
    stock: conint(ge=0)

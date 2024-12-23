from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import Product as ProductModel
from .schemas import Product, ProductCreate, ProductUpdate, ProductStockUpdate
from ..auth.middleware import check_permissions

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    _=Depends(check_permissions(["admin"]))
):
    """Crear un nuevo producto."""
    db_product = ProductModel(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/", response_model=List[Product])
async def get_products(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = Query(None, description="Filtrar por categoría"),
    active_only: bool = Query(True, description="Solo mostrar productos activos"),
    db: Session = Depends(get_db),
    _=Depends(check_permissions(["admin", "cashier", "cook"]))
):
    """Obtener todos los productos con filtros opcionales."""
    query = db.query(ProductModel)

    if active_only:
        query = query.filter(ProductModel.is_active == True)

    if category:
        query = query.filter(ProductModel.category == category)

    products = query.offset(skip).limit(limit).all()
    return products

@router.get("/categories")
async def get_categories(
    db: Session = Depends(get_db),
    _=Depends(check_permissions(["admin", "cashier", "cook"]))
):
    """Obtener todas las categorías únicas."""
    categories = db.query(ProductModel.category).distinct().all()
    return [category[0] for category in categories]

@router.get("/{product_id}", response_model=Product)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    _=Depends(check_permissions(["admin", "cashier", "cook"]))
):
    """Obtener un producto específico."""
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product

@router.patch("/{product_id}", response_model=Product)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    _=Depends(check_permissions(["admin"]))
):
    """Actualizar un producto."""
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    update_data = product_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)
    return db_product

@router.patch("/{product_id}/stock", response_model=Product)
async def update_product_stock(
    product_id: int,
    stock_update: ProductStockUpdate,
    db: Session = Depends(get_db),
    _=Depends(check_permissions(["admin", "cook"]))
):
    """Actualizar el stock de un producto."""
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    db_product.stock = stock_update.stock
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _=Depends(check_permissions(["admin"]))
):
    """Eliminar un producto (desactivación lógica)."""
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    db_product.is_active = False
    db.commit()
    return None

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Table as TableModel
from .schemas import Table, TableCreate, TableUpdate, TableStatusUpdate
from ..auth.middleware import check_permissions

router = APIRouter(
    prefix="/tables",
    tags=["tables"]
)

@router.post("/", response_model=Table, status_code=status.HTTP_201_CREATED)
async def create_table(
    table: TableCreate,
    db: Session = Depends(get_db),
    _=Depends(check_permissions(["admin", "cashier"]))
):
    """Crear una nueva mesa."""
    db_table = TableModel(
        capacity=table.capacity
    )
    db.add(db_table)
    db.commit()
    db.refresh(db_table)
    return db_table

@router.get("/", response_model=List[Table])
async def get_tables(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(check_permissions(["admin", "cashier", "cook"]))
):
    """Obtener todas las mesas."""
    tables = db.query(TableModel).offset(skip).limit(limit).all()
    return tables

@router.get("/{table_id}", response_model=Table)
async def get_table(
    table_id: int,
    db: Session = Depends(get_db),
    _=Depends(check_permissions(["admin", "cashier", "cook"]))
):
    """Obtener una mesa específica."""
    table = db.query(TableModel).filter(TableModel.id == table_id).first()
    if table is None:
        raise HTTPException(status_code=404, detail="Mesa no encontrada")
    return table

@router.patch("/{table_id}", response_model=Table)
async def update_table(
    table_id: int,
    table_update: TableUpdate,
    db: Session = Depends(get_db),
    _=Depends(check_permissions(["admin", "cashier"]))
):
    """Actualizar una mesa."""
    db_table = db.query(TableModel).filter(TableModel.id == table_id).first()
    if db_table is None:
        raise HTTPException(status_code=404, detail="Mesa no encontrada")

    update_data = table_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_table, key, value)

    db.commit()
    db.refresh(db_table)
    return db_table

@router.patch("/{table_id}/status", response_model=Table)
async def update_table_status(
    table_id: int,
    status_update: TableStatusUpdate,
    db: Session = Depends(get_db),
    _=Depends(check_permissions(["admin", "cashier"]))
):
    """Actualizar el estado de una mesa."""
    db_table = db.query(TableModel).filter(TableModel.id == table_id).first()
    if db_table is None:
        raise HTTPException(status_code=404, detail="Mesa no encontrada")

    db_table.status = status_update.status
    db.commit()
    db.refresh(db_table)
    return db_table

@router.delete("/{table_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_table(
    table_id: int,
    db: Session = Depends(get_db),
    _=Depends(check_permissions(["admin"]))
):
    """Eliminar una mesa (desactivación lógica)."""
    db_table = db.query(TableModel).filter(TableModel.id == table_id).first()
    if db_table is None:
        raise HTTPException(status_code=404, detail="Mesa no encontrada")

    db_table.is_active = False
    db.commit()
    return None

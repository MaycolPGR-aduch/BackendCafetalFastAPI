from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.core.db import get_db
from pydantic import BaseModel  # <-- Agrega esta línea

router = APIRouter()

class MovementIn(BaseModel):  # <-- Cambia dict por BaseModel
    warehouse_id: int
    product_id: int
    uom_id: int
    movement_type: str
    qty: float
    lot_id: int | None = None
    ref_type: str | None = None
    ref_id: int | None = None
    notes: str | None = None

@router.post("/movements")
def create_movement(payload: MovementIn, db: Session = Depends(get_db)):
    # Ya no necesitas validar los campos requeridos, Pydantic lo hace automáticamente

    # Validación OUT: saldo suficiente (si qty < 0)
    if payload.qty < 0:
        # saldo actual en v_CurrentStock
        sql = """
        SELECT SUM(qty_on_hand) FROM cafetal.v_CurrentStock
        WHERE warehouse_id=:w AND product_id=:p AND (lot_id=:l OR (:l IS NULL AND lot_id IS NULL))
        """
        saldo = db.execute(
            text(sql),
            {"w": payload.warehouse_id, "p": payload.product_id, "l": payload.lot_id}
        ).scalar() or 0.0
        if saldo + payload.qty < 0:
            raise HTTPException(409, "Stock insuficiente para salida.")

    ins = """
    INSERT INTO cafetal.InventoryMovement (warehouse_id, product_id, lot_id, qty, uom_id, movement_type, ref_type, ref_id, notes)
    VALUES (:warehouse_id, :product_id, :lot_id, :qty, :uom_id, :movement_type, :ref_type, :ref_id, :notes)
    """
    db.execute(text(ins), payload.dict())
    db.commit()
    return {"ok": True}

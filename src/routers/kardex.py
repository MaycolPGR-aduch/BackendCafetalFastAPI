from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.core.db import get_db

router = APIRouter()

SQL = """
SELECT im.movement_ts, im.movement_type, im.qty, u.code AS uom_code,
       im.notes, im.ref_type, im.ref_id,
       w.code AS wh_code, p.sku, p.name AS product_name, l.lot_code
FROM cafetal.InventoryMovement im
JOIN cafetal.Warehouse w ON w.warehouse_id = im.warehouse_id
JOIN cafetal.Product   p ON p.product_id   = im.product_id
JOIN cafetal.UnitOfMeasure u ON u.uom_id   = im.uom_id
LEFT JOIN cafetal.Lot l ON l.lot_id = im.lot_id
WHERE 1=1
"""

@router.get("/inventory/kardex")
def get_kardex(
    db: Session = Depends(get_db),
    warehouseId: int | None = None,
    productId: int | None = None,
    lotId: int | None = None,
    dateFrom: str | None = None,  # "dd/MM/yyyy"
    dateTo: str | None = None
):
    params = {}
    sql = SQL
    if warehouseId: sql += " AND im.warehouse_id = :warehouseId"; params["warehouseId"] = warehouseId
    if productId:   sql += " AND im.product_id = :productId"; params["productId"] = productId
    if lotId:       sql += " AND im.lot_id = :lotId"; params["lotId"] = lotId
    if dateFrom:
        sql += " AND CONVERT(date, im.movement_ts) >= CONVERT(date, :from, 103)"
        params["from"] = dateFrom
    if dateTo:
        sql += " AND CONVERT(date, im.movement_ts) <= CONVERT(date, :to, 103)"
        params["to"] = dateTo

    sql += " ORDER BY im.movement_ts"
    rows = db.execute(text(sql), params).mappings().all()
    out = []
    for r in rows:
        out.append({
            "datetime": r["movement_ts"].strftime("%d/%m/%Y %H:%M"),
            "type": r["movement_type"],
            "qty": float(r["qty"]),
            "uom": r["uom_code"],
            "warehouse": r["wh_code"],
            "product": {"sku": r["sku"], "name": r["product_name"]},
            "lot": r["lot_code"],
            "ref": {"type": r["ref_type"], "id": r["ref_id"]},
            "notes": r["notes"]
        })
    return out

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.core.db import get_db

router = APIRouter()

# Utilizamos la vista cafetal.v_CurrentStock para saldos
BASE_SQL = """
SELECT s.warehouse_id, s.product_id, s.lot_id, s.qty_on_hand,
       w.code AS wh_code, w.name AS wh_name,
       p.sku, p.name AS product_name,
       c.name AS category_name,
       u.code AS uom_code,
       l.lot_code, l.production_date, l.expiration_date, l.quality_status
FROM cafetal.v_CurrentStock s
JOIN cafetal.Warehouse w ON w.warehouse_id = s.warehouse_id
JOIN cafetal.Product   p ON p.product_id   = s.product_id
JOIN cafetal.ProductCategory c ON c.category_id = p.category_id
JOIN cafetal.UnitOfMeasure u ON u.uom_id = p.uom_id
LEFT JOIN cafetal.Lot   l ON l.lot_id     = s.lot_id
WHERE 1=1
"""

def apply_filters(sql: str, params: dict, warehouseId: int|None, category: str|None, quality: str|None, search: str|None):
    if warehouseId: 
        sql += " AND s.warehouse_id = :warehouseId"
        params["warehouseId"] = warehouseId
    if category:
        sql += " AND c.name = :category"
        params["category"] = category
    if quality:
        sql += " AND l.quality_status = :quality"
        params["quality"] = quality
    if search:
        sql += " AND (p.name LIKE :search OR p.sku LIKE :search OR l.lot_code LIKE :search)"
        params["search"] = f"%{search}%"
    return sql, params

@router.get("/inventory")
def get_inventory(
    db: Session = Depends(get_db),
    warehouseId: int | None = None,
    category: str | None = None,
    quality: str | None = None,
    search: str | None = None,
    page: int = 1,
    pageSize: int = 25
):
    params = {}
    sql, params = apply_filters(BASE_SQL, params, warehouseId, category, quality, search)

    # total
    count_sql = f"SELECT COUNT(1) AS cnt FROM ({sql}) q"
    total = db.execute(text(count_sql), params).scalar() or 0

    # page
    offset = (page - 1) * pageSize
    page_sql = sql + " ORDER BY p.name OFFSET :off ROWS FETCH NEXT :lim ROWS ONLY"
    params.update({"off": offset, "lim": pageSize})
    rows = db.execute(text(page_sql), params).mappings().all()

    items = []
    for r in rows:
        available = float(r["qty_on_hand"] or 0.0)
        total_qty = available  # si manejas reservado en otra tabla, aquí ajustas
        reserved = 0.0
        items.append({
            "id": f"{r['warehouse_id']}-{r['product_id']}-{r['lot_id'] or 'NULL'}",
            "warehouse": {"id": r["warehouse_id"], "code": r["wh_code"], "name": r["wh_name"]},
            "product": {"id": r["product_id"], "sku": r["sku"], "name": r["product_name"], "category": r["category_name"], "uom": r["uom_code"]},
            "lot": {
                "id": r["lot_id"],
                "code": r["lot_code"],
                "qualityStatus": r["quality_status"],
                "mfgDate": r["production_date"].strftime("%d/%m/%Y") if r["production_date"] else None,
                "expDate": r["expiration_date"].strftime("%d/%m/%Y") if r["expiration_date"] else None
            },
            "qty": {"total": total_qty, "available": available, "reserved": reserved},
            "cost": None,
            "lastMovement": None
        })
    return {"items": items, "page": page, "pageSize": pageSize, "total": total}

@router.get("/inventory/kpis")
def get_inventory_kpis(
    db: Session = Depends(get_db),
    warehouseId: int | None = None,
    category: str | None = None,
    quality: str | None = None,
    search: str | None = None
):
    params = {}
    sql, params = apply_filters(BASE_SQL, params, warehouseId, category, quality, search)
    sum_sql = f"SELECT SUM(qty_on_hand) AS sum_qty FROM ({sql}) q"
    sum_qty = float(db.execute(text(sum_sql), params).scalar() or 0.0)

    # Para MVP: disponible = total, reservado = 0 (luego integraremos reservas reales)
    available = sum_qty
    reserved = 0.0

    # Alertas por regla simple (<=20% crítico, <=50% bajo) a partir de filas individuales
    rows = db.execute(text(sql), params).mappings().all()
    critical = 0; low = 0
    for r in rows:
        total_row = float(r["qty_on_hand"] or 0.0)
        if total_row <= 0: continue
        pct = (total_row / total_row) * 100  # placeholder; cuando haya min_stock, calculamos vs mínimo
        # Para demo, marcamos low/critical si el saldo es muy bajo:
        if total_row <= 20: critical += 1
        elif total_row <= 50: low += 1

    return {
        "totalStock": {"qty": sum_qty, "uom": "kg"},
        "availableStock": {"qty": available, "uom": "kg", "pct": 100.0 if sum_qty==0 else round(available/sum_qty*100,1)},
        "reservedStock": {"qty": reserved, "uom": "kg", "pct": 0.0},
        "alerts": {"critical": critical, "low": low}
    }

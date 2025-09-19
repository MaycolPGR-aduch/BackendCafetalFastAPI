# src/routers/dashboard.py
from datetime import date
from typing import Any, List, Dict

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..schemas.dashboard import (
    DashboardOverview, KPIBlock, Series, Alerts
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


# Helper: ejecuta SQL y devuelve lista de dicts
def db_rows(db: Session, sql: str, params: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
    res = db.execute(text(sql), params or {})
    cols = res.keys()
    return [dict(zip(cols, r)) for r in res.fetchall()]


@router.get("/overview", response_model=DashboardOverview)
def overview(db: Session = Depends(get_db)) -> DashboardOverview:
    # =========================
    # KPIs (ajustados a tu schema)
    # =========================

    # Ventas del mes (Invoice.type='SALES')
    k_ventas = db_rows(db, """
        SELECT SUM(i.total_amount) AS total
        FROM cafetal.Invoice i
        WHERE i.type = 'SALES'
          AND YEAR(i.invoice_date) = YEAR(GETDATE())
          AND MONTH(i.invoice_date) = MONTH(GETDATE())
    """)[0]["total"] or 0

    # Stock total (desde movimientos). Ajusta los tipos IN/OUT según tu data.
    # IN: PURCHASE, TRANSFER_IN, RETURN_SALE, ADJUST_IN, PROD_IN
    # OUT: SALE, TRANSFER_OUT, RETURN_PURCHASE, ADJUST_OUT, PROD_OUT
    k_stock = db_rows(db, """
        SELECT CAST(SUM(
          CASE
            WHEN im.movement_type IN ('PURCHASE','TRANSFER_IN','RETURN_SALE','ADJUST_IN','PROD_IN') THEN ISNULL(im.qty,0)
            WHEN im.movement_type IN ('SALE','TRANSFER_OUT','RETURN_PURCHASE','ADJUST_OUT','PROD_OUT') THEN -ISNULL(im.qty,0)
            ELSE 0
          END
        ) AS DECIMAL(18,2)) AS stock_total
        FROM cafetal.InventoryMovement im
    """)[0]["stock_total"] or 0

    # % lotes aprobados últimos 12 meses (QualityTest.passed 1/0) usando sample_date
    k_lotes_pct = db_rows(db, """
        SELECT CAST(
          CASE WHEN COUNT(*) = 0 THEN 0
               ELSE 100.0 * SUM(CASE WHEN qt.passed = 1 THEN 1 ELSE 0 END) / COUNT(*)
          END AS DECIMAL(10,2)) AS pct
        FROM cafetal.QualityTest qt
        WHERE qt.sample_date >= DATEADD(MONTH, -12, GETDATE())
    """)[0]["pct"] or 0

    # % entregas cumplidas = entregas DELIVERED / total últimas 12m (no hay promised_date)
    k_entregas_pct = db_rows(db, """
        SELECT CAST(
          CASE WHEN COUNT(*) = 0 THEN 0
               ELSE 100.0 * SUM(CASE WHEN s.status = 'DELIVERED' THEN 1 ELSE 0 END) / COUNT(*)
          END AS DECIMAL(10,2)) AS pct
        FROM cafetal.Shipment s
        WHERE s.ship_date >= DATEADD(MONTH, -12, GETDATE())
    """)[0]["pct"] or 0

    # Costo de producción del mes (CostRecord.amount por date_ocurred)
    k_costo = db_rows(db, """
        SELECT SUM(c.amount) AS total
        FROM cafetal.CostRecord c
        WHERE YEAR(c.date_occurred) = YEAR(GETDATE())
          AND MONTH(c.date_occurred) = MONTH(GETDATE())
    """)[0]["total"] or 0

    # Nómina del mes: tu tabla PayrollRun está vacía → lo dejamos en 0
    k_nomina = 0

    kpis = KPIBlock(
        ventas_mes=float(k_ventas or 0),
        delta_ventas_mes=0,  # pendiente: comparar contra mes anterior si quieres
        stock_total_kg=float(k_stock or 0),
        lotes_aprobados_pct=float(k_lotes_pct or 0),
        delta_lotes_aprobados=0,
        entregas_a_tiempo_pct=float(k_entregas_pct or 0),
        delta_entregas=0,
        costo_produccion_mes=float(k_costo or 0),
        delta_costo_produccion=0,
        nomina_mes=float(k_nomina or 0),
    )

    # =========================
    # Series (últimos 12 meses)
    # =========================

    ventas_mes = db_rows(db, """
        SELECT FORMAT(i.invoice_date,'yyyy-MM') AS ym,
               SUM(i.total_amount) AS total
        FROM cafetal.Invoice i
        WHERE i.type = 'SALES'
          AND i.invoice_date >= DATEADD(MONTH, -11, DATEFROMPARTS(YEAR(GETDATE()), MONTH(GETDATE()), 1))
        GROUP BY FORMAT(i.invoice_date,'yyyy-MM')
        ORDER BY ym
    """)

    stock_cat = db_rows(db, """
        WITH stock AS (
          SELECT p.category_id,
                 SUM(
                   CASE
                     WHEN im.movement_type IN ('PURCHASE','TRANSFER_IN','RETURN_SALE','ADJUST_IN','PROD_IN') THEN ISNULL(im.qty,0)
                     WHEN im.movement_type IN ('SALE','TRANSFER_OUT','RETURN_PURCHASE','ADJUST_OUT','PROD_OUT') THEN -ISNULL(im.qty,0)
                     ELSE 0
                   END
                 ) AS qty
          FROM cafetal.Product p
          LEFT JOIN cafetal.InventoryMovement im ON im.product_id = p.product_id
          GROUP BY p.category_id
        )
        SELECT COALESCE(pc.name,'Sin categoría') AS categoria,
               CAST(ISNULL(s.qty,0) AS DECIMAL(18,2)) AS kg
        FROM stock s
        LEFT JOIN cafetal.ProductCategory pc ON pc.category_id = s.category_id
        ORDER BY categoria
    """)

    calidad = db_rows(db, """
        SELECT FORMAT(qt.sample_date,'yyyy-MM') AS ym,
               CAST(
                 CASE WHEN COUNT(*)=0 THEN 0
                      ELSE 100.0 * SUM(CASE WHEN qt.passed=1 THEN 1 ELSE 0 END) / COUNT(*)
                 END AS DECIMAL(10,2)
               ) AS pct
        FROM cafetal.QualityTest qt
        WHERE qt.sample_date >= DATEADD(MONTH, -11, DATEFROMPARTS(YEAR(GETDATE()), MONTH(GETDATE()), 1))
        GROUP BY FORMAT(qt.sample_date,'yyyy-MM')
        ORDER BY ym
    """)

    top_prod = db_rows(db, """
        SELECT TOP 10 p.name AS producto,
               SUM(ii.qty) AS qty
        FROM cafetal.InvoiceItem ii
        JOIN cafetal.Invoice i  ON i.invoice_id  = ii.invoice_id AND i.type='SALES'
        JOIN cafetal.Product p  ON p.product_id  = ii.product_id
        WHERE i.invoice_date >= DATEADD(MONTH, -12, GETDATE())
        GROUP BY p.name
        ORDER BY qty DESC, p.name
    """)

    series = Series(
        ventas_por_mes=[{"ym": r["ym"], "total": float(r["total"] or 0)} for r in ventas_mes],
        stock_por_categoria=[{"categoria": r["categoria"], "kg": float(r["kg"] or 0)} for r in stock_cat],
        tasa_aprobacion_calidad=[{"ym": r["ym"], "pct": float(r["pct"] or 0)} for r in calidad],
        top_productos_vendidos=[{"producto": r["producto"], "qty": float(r["qty"] or 0)} for r in top_prod],
    )

    # =========================
    # Alertas
    # =========================

    # Stock bajo: TOP 10 productos con menor stock (no usas min_stock)
    stock_bajo = db_rows(db, """
        WITH stock AS (
          SELECT p.product_id, p.name,
                 SUM(
                   CASE
                     WHEN im.movement_type IN ('PURCHASE','TRANSFER_IN','RETURN_SALE','ADJUST_IN','PROD_IN') THEN ISNULL(im.qty,0)
                     WHEN im.movement_type IN ('SALE','TRANSFER_OUT','RETURN_PURCHASE','ADJUST_OUT','PROD_OUT') THEN -ISNULL(im.qty,0)
                     ELSE 0
                   END
                 ) AS qty
          FROM cafetal.Product p
          LEFT JOIN cafetal.InventoryMovement im ON im.product_id = p.product_id
          GROUP BY p.product_id, p.name
        )
        SELECT TOP 10 product_id, name, CAST(ISNULL(qty,0) AS DECIMAL(18,2)) AS qty
        FROM stock
        ORDER BY qty ASC, name
    """)

    # OP atrasadas: status no COMpletadas y started_at hace > 7 días (ajústalo si deseas)
    op_atrasadas = db_rows(db, """
        SELECT po.production_order_id, po.order_code, po.status, po.started_at
        FROM cafetal.ProductionOrder po
        WHERE (po.status IS NULL OR po.status NOT IN ('DONE','CANCELED'))
          AND po.started_at IS NOT NULL
          AND po.started_at < DATEADD(DAY, -7, GETDATE())
        ORDER BY po.started_at
    """)

    # Facturas vencidas: due_date < hoy y status distinto a PAID
    fact_vencidas = db_rows(db, """
        SELECT i.invoice_id, i.inv_code, i.due_date, i.total_amount, i.status
        FROM cafetal.Invoice i
        WHERE i.due_date IS NOT NULL
          AND i.due_date < CONVERT(date, GETDATE())
          AND (i.status IS NULL OR i.status <> 'PAID')
        ORDER BY i.due_date
    """)

    # Lotes pendientes: QualityTest con passed NULL (si no hay “pendiente” explícito)
    lotes_pend = db_rows(db, """
        SELECT qt.quality_test_id, qt.lot_id, qt.sample_date
        FROM cafetal.QualityTest qt
        WHERE qt.passed IS NULL
        ORDER BY qt.sample_date
    """)

    alertas = Alerts(
        stock_bajo=stock_bajo,
        orden_produccion_atrasada=op_atrasadas,
        facturas_vencidas=fact_vencidas,
        lotes_pendientes_aprobacion=lotes_pend,
    )

    return DashboardOverview(kpis=kpis, series=series, alertas=alertas)


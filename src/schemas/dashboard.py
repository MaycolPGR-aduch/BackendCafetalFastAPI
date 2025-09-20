from pydantic import BaseModel
from typing import List, Dict, Any

class KPIBlock(BaseModel):
    ventas_mes: float
    delta_ventas_mes: float
    stock_total_kg: float
    lotes_aprobados_pct: float
    delta_lotes_aprobados: float
    entregas_a_tiempo_pct: float
    delta_entregas: float
    costo_produccion_mes: float
    delta_costo_produccion: float
    nomina_mes: float

class Series(BaseModel):
    ventas_por_mes: List[Dict[str, Any]]
    stock_por_categoria: List[Dict[str, Any]]
    tasa_aprobacion_calidad: List[Dict[str, Any]]
    top_productos_vendidos: List[Dict[str, Any]]

class Alerts(BaseModel):
    stock_bajo: List[Dict[str, Any]]
    orden_produccion_atrasada: List[Dict[str, Any]]
    facturas_vencidas: List[Dict[str, Any]]
    lotes_pendientes_aprobacion: List[Dict[str, Any]]

class DashboardOverview(BaseModel):
    kpis: KPIBlock
    series: Series
    alertas: Alerts



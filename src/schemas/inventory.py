from pydantic import BaseModel
from typing import Optional, List

class WarehouseOut(BaseModel):
    id: int
    code: str
    name: str
    class Config: from_attributes = True

class ProductOut(BaseModel):
    id: int
    sku: str
    name: str
    category: str
    uom: str

class LotOut(BaseModel):
    id: int
    code: str
    qualityStatus: str
    mfgDate: Optional[str] = None
    expDate: Optional[str] = None

class InventoryRow(BaseModel):
    id: str
    warehouse: WarehouseOut
    product: ProductOut
    lot: LotOut
    qty: dict  # {total, available, reserved}
    cost: Optional[dict] = None
    lastMovement: Optional[str] = None

class InventoryPage(BaseModel):
    items: List[InventoryRow]
    page: int
    pageSize: int
    total: int

class KpiOut(BaseModel):
    totalStock: dict
    availableStock: dict
    reservedStock: dict
    alerts: dict

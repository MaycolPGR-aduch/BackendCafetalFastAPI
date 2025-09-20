# src/schemas/rrhh.py
from typing import Optional, Literal
from pydantic import BaseModel

class EmpleadoOut(BaseModel):
    id: int
    doc_id: Optional[str] = None
    nombres: str
    apellidos: str
    email: Optional[str] = None
    telefono: Optional[str] = None
    position_id: Optional[int] = None
    base_salary: Optional[float] = None
    contract_type: Optional[str] = None
    contract_start: Optional[str] = None  # lo devolvemos como isoformat() desde el router
    contract_end: Optional[str] = None
    estado: Literal["activo", "inactivo"]
    fecha_ingreso: Optional[str] = None   # idem isoformat() desde el router

class EmpleadosPage(BaseModel):
    items: list[EmpleadoOut]
    page: int
    page_size: int
    total: int

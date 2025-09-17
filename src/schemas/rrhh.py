from datetime import date
from typing import List
from pydantic import BaseModel, EmailStr

class EmpleadoOut(BaseModel):
    id: int
    nombres: str
    apellidos: str
    email: EmailStr
    estado: str  # "activo" | "inactivo"
    fecha_ingreso: date

class EmpleadosPage(BaseModel):
    items: List[EmpleadoOut]
    page: int
    page_size: int
    total: int

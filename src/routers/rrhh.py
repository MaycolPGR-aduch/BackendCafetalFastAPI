from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Query
from ..schemas.rrhh import EmpleadoOut, EmpleadosPage

router = APIRouter()

# Datos fake para arrancar
_FAKE_EMPLEADOS: List[EmpleadoOut] = [
    EmpleadoOut(id=1, nombres="Ana",  apellidos="Pérez",   email="ana.perez@cafe.com",  estado="activo",   fecha_ingreso=date(2023, 3, 10)),
    EmpleadoOut(id=2, nombres="Luis", apellidos="García",  email="luis.garcia@cafe.com", estado="activo",  fecha_ingreso=date(2022, 11, 5)),
    EmpleadoOut(id=3, nombres="Eva",  apellidos="Rojas",   email="eva.rojas@cafe.com",  estado="inactivo", fecha_ingreso=date(2021, 7, 20)),
    EmpleadoOut(id=4, nombres="Katy", apellidos="Vargas",  email="katy.vargas@cafe.com", estado="activo",  fecha_ingreso=date(2024, 1, 15)),
]

@router.get("/empleados", response_model=EmpleadosPage, summary="Listar empleados (fake)")
def list_empleados(
    q: Optional[str] = Query(None, description="Búsqueda por nombre/apellido/email"),
    status: Optional[str] = Query(None, description="Filtro por estado: activo|inactivo"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    data = _FAKE_EMPLEADOS

    # filtro por texto
    if q:
        qlow = q.lower()
        data = [
            e for e in data
            if (qlow in e.nombres.lower()
                or qlow in e.apellidos.lower()
                or qlow in e.email.lower())
        ]

    # filtro por estado
    if status:
        status = status.lower()
        data = [e for e in data if e.estado.lower() == status]

    total = len(data)
    start = (page - 1) * page_size
    end = start + page_size
    items = data[start:end]

    return EmpleadosPage(items=items, page=page, page_size=page_size, total=total)

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Table, MetaData, select, func, or_
from ..core.db import engine, get_db
from ..schemas.rrhh import EmpleadoOut, EmpleadosPage
import logging

router = APIRouter()
log = logging.getLogger("rrhh")

# Reflejo de tabla
metadata = MetaData()
Employee = Table("Employee", metadata, schema="cafetal", autoload_with=engine)

@router.get("/rrhh/empleados", response_model=EmpleadosPage)
def list_empleados(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=200),
    q: str | None = Query(None, description="Buscar por nombre, apellido, email o documento"),
    db: Session = Depends(get_db),
):
    try:
        # SELECT base
        base_stmt = select(
            Employee.c.employee_id,
            Employee.c.doc_id,
            Employee.c.first_name,
            Employee.c.last_name,
            Employee.c.email,
            Employee.c.phone,
            Employee.c.hire_date,
            Employee.c.position_id,
            Employee.c.base_salary,
            Employee.c.status,
            Employee.c.contract_type,
            Employee.c.contract_start,
            Employee.c.contract_end,
        )

        if q:
            ql = f"%{q.lower()}%"
            base_stmt = base_stmt.where(
                or_(
                    func.lower(Employee.c.first_name).like(ql),
                    func.lower(Employee.c.last_name).like(ql),
                    func.lower(Employee.c.email).like(ql),
                    func.lower(Employee.c.doc_id).like(ql),
                )
            )

        # Total con mismos filtros
        total_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = db.execute(total_stmt).scalar() or 0

        # Orden + paginación
        stmt = (
            base_stmt.order_by(Employee.c.employee_id)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = db.execute(stmt).all()

        items: list[EmpleadoOut] = []
        for r in rows:
            # Normalizaciones seguras para JSON
            base_salary = float(r.base_salary) if r.base_salary is not None else None
            hire_date = r.hire_date.isoformat() if getattr(r, "hire_date", None) else None
            contract_start = (
                r.contract_start.isoformat() if getattr(r, "contract_start", None) else None
            )
            contract_end = (
                r.contract_end.isoformat() if getattr(r, "contract_end", None) else None
            )

            items.append(
                EmpleadoOut(
                    id=r.employee_id,
                    doc_id=r.doc_id,
                    nombres=r.first_name,
                    apellidos=r.last_name,
                    email=r.email,
                    telefono=r.phone,
                    position_id=r.position_id,
                    base_salary=base_salary,
                    contract_type=r.contract_type,
                    contract_start=contract_start,
                    contract_end=contract_end,
                    estado="activo" if (r.status or "").upper() == "ACTIVE" else "inactivo",
                    fecha_ingreso=hire_date,
                )
            )

        return EmpleadosPage(items=items, page=page, page_size=page_size, total=total)

    except Exception as e:
        # Traza en consola del backend
        log.exception("Error en /rrhh/empleados")
        # Detalle visible en la respuesta (temporal para diagnóstico)
        raise HTTPException(status_code=500, detail=f"RRHH: {type(e).__name__}: {e}")

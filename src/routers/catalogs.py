from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.core.db import get_db
from src.models.inventory import Warehouse, UnitOfMeasure, Product, ProductCategory

router = APIRouter()

@router.get("/warehouses")
def list_warehouses(db: Session = Depends(get_db)):
    rows = db.query(Warehouse).all()
    return [{"id": w.warehouse_id, "code": w.code, "name": w.name} for w in rows]

@router.get("/uoms")
def list_uoms(db: Session = Depends(get_db)):
    rows = db.query(UnitOfMeasure).all()
    return [{"id": u.uom_id, "code": u.code, "description": u.description} for u in rows]

@router.get("/products")
def list_products(db: Session = Depends(get_db), search: str | None = None, category: str | None = None):
    q = db.query(Product, ProductCategory, UnitOfMeasure)\
         .join(ProductCategory, Product.category_id==ProductCategory.category_id)\
         .join(UnitOfMeasure, Product.uom_id==UnitOfMeasure.uom_id)
    if search:
        like = f"%{search}%"
        q = q.filter((Product.name.ilike(like)) | (Product.sku.ilike(like)))
    if category:
        q = q.filter(ProductCategory.name==category)
    res = []
    for p, c, u in q.limit(200):
        res.append({"id": p.product_id, "sku": p.sku, "name": p.name, "category": c.name, "uom": u.code})
    return res

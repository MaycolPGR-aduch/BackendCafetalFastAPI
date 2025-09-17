from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from src.core.db import Base

class UnitOfMeasure(Base):
    __tablename__ = "UnitOfMeasure"
    __table_args__ = {"schema": "cafetal"}
    uom_id = Column(Integer, primary_key=True)
    code = Column(String(10), nullable=False)
    description = Column(String(50), nullable=False)

class ProductCategory(Base):
    __tablename__ = "ProductCategory"
    __table_args__ = {"schema": "cafetal"}
    category_id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)

class Product(Base):
    __tablename__ = "Product"
    __table_args__ = {"schema": "cafetal"}
    product_id = Column(Integer, primary_key=True)
    sku = Column(String(30), nullable=False)
    name = Column(String(150), nullable=False)
    category_id = Column(Integer, ForeignKey("cafetal.ProductCategory.category_id"), nullable=False)
    uom_id = Column(Integer, ForeignKey("cafetal.UnitOfMeasure.uom_id"), nullable=False)
    product_type = Column(String(20), nullable=False)

class Warehouse(Base):
    __tablename__ = "Warehouse"
    __table_args__ = {"schema": "cafetal"}
    warehouse_id = Column(Integer, primary_key=True)
    code = Column(String(20), nullable=False)
    name = Column(String(120), nullable=False)
    location = Column(String(150))

class Lot(Base):
    __tablename__ = "Lot"
    __table_args__ = {"schema": "cafetal"}
    lot_id = Column(Integer, primary_key=True)
    lot_code = Column(String(30), nullable=False)
    product_id = Column(Integer, ForeignKey("cafetal.Product.product_id"), nullable=False)
    uom_id = Column(Integer, ForeignKey("cafetal.UnitOfMeasure.uom_id"), nullable=False)
    production_date = Column(Date)
    expiration_date = Column(Date)
    quality_status = Column(String(12), nullable=False)
    qty_initial = Column(Numeric(18,3), nullable=False)
    qty_available = Column(Numeric(18,3), nullable=False)

class InventoryMovement(Base):
    __tablename__ = "InventoryMovement"
    __table_args__ = {"schema": "cafetal"}
    movement_id = Column(Integer, primary_key=True)
    movement_ts = Column(DateTime, nullable=False)
    warehouse_id = Column(Integer, ForeignKey("cafetal.Warehouse.warehouse_id"), nullable=False)
    product_id = Column(Integer, ForeignKey("cafetal.Product.product_id"), nullable=False)
    lot_id = Column(Integer, ForeignKey("cafetal.Lot.lot_id"))
    qty = Column(Numeric(18,3), nullable=False)
    uom_id = Column(Integer, ForeignKey("cafetal.UnitOfMeasure.uom_id"), nullable=False)
    movement_type = Column(String(20), nullable=False)
    ref_type = Column(String(20))
    ref_id = Column(Integer)
    notes = Column(String(250))

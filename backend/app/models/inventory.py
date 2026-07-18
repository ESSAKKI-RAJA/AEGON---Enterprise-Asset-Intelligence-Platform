from __future__ import annotations
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, Float, ForeignKey, DateTime, Enum, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import AuditableBase
from app.models.enums import InventoryStatus

class Warehouse(AuditableBase):
    """
    Physical locations where spare parts and inventory stock are held.
    """
    __tablename__ = "warehouses"

    name: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    items: Mapped[List["InventoryItem"]] = relationship("InventoryItem", back_populates="warehouse", cascade="all, delete-orphan")
    transfers_from: Mapped[List["InventoryTransfer"]] = relationship("InventoryTransfer", foreign_keys="InventoryTransfer.from_warehouse_id", back_populates="from_warehouse")
    transfers_to: Mapped[List["InventoryTransfer"]] = relationship("InventoryTransfer", foreign_keys="InventoryTransfer.to_warehouse_id", back_populates="to_warehouse")

class InventoryItem(AuditableBase):
    """
    Individually tracked stock items, parts or supplies.
    """
    __tablename__ = "inventory_items"
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="quantity_non_negative"),
        CheckConstraint("reorder_level >= 0", name="reorder_level_non_negative"),
    )

    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    sku: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reorder_level: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[InventoryStatus] = mapped_column(Enum(InventoryStatus), default=InventoryStatus.IN_STOCK, nullable=False)
    warehouse_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False)

    warehouse: Mapped["Warehouse"] = relationship("Warehouse", back_populates="items")
    transactions: Mapped[List["InventoryTransaction"]] = relationship("InventoryTransaction", back_populates="item", cascade="all, delete-orphan")
    adjustments: Mapped[List["InventoryAdjustment"]] = relationship("InventoryAdjustment", back_populates="item", cascade="all, delete-orphan")
    consumptions: Mapped[List["InventoryConsumption"]] = relationship("InventoryConsumption", back_populates="item", cascade="all, delete-orphan")
    reservations: Mapped[List["InventoryReservation"]] = relationship("InventoryReservation", back_populates="item", cascade="all, delete-orphan")
    stock_alerts: Mapped[List["StockAlert"]] = relationship("StockAlert", back_populates="item", cascade="all, delete-orphan")

class InventoryTransaction(AuditableBase):
    """
    Auditing standard stock movements (IN/OUT).
    """
    __tablename__ = "inventory_transactions"

    item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("inventory_items.id", ondelete="CASCADE"), nullable=False, index=True)
    transaction_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. RECEIPT, ISSUE, ADJUSTMENT
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_cost: Mapped[float] = mapped_column(Float, nullable=False)
    reference_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # PO reference or custom code

    item: Mapped["InventoryItem"] = relationship("InventoryItem", back_populates="transactions")

class InventoryAdjustment(AuditableBase):
    """
    Manual adjustments made to resolve audit discrepancies.
    """
    __tablename__ = "inventory_adjustments"

    item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("inventory_items.id", ondelete="CASCADE"), nullable=False, index=True)
    adjusted_quantity: Mapped[int] = mapped_column(Integer, nullable=False) # e.g. -2 or +5
    reason: Mapped[str] = mapped_column(String(255), nullable=False)

    item: Mapped["InventoryItem"] = relationship("InventoryItem", back_populates="adjustments")

class InventoryConsumption(AuditableBase):
    """
    Log track for stock items utilized in work orders or department operations.
    """
    __tablename__ = "inventory_consumptions"

    item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("inventory_items.id", ondelete="CASCADE"), nullable=False, index=True)
    work_order_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("work_orders.id", ondelete="SET NULL"), nullable=True)
    quantity_used: Mapped[int] = mapped_column(Integer, nullable=False)
    consumed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    item: Mapped["InventoryItem"] = relationship("InventoryItem", back_populates="consumptions")
    work_order: Mapped[Optional["WorkOrder"]] = relationship("WorkOrder", back_populates="consumptions")

class InventoryTransfer(AuditableBase):
    """
    Fulfilling transfers of parts between different warehouses.
    """
    __tablename__ = "inventory_transfers"

    from_warehouse_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("warehouses.id", ondelete="RESTRICT"), nullable=False)
    to_warehouse_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("warehouses.id", ondelete="RESTRICT"), nullable=False)
    item_sku: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False)

    from_warehouse: Mapped["Warehouse"] = relationship("Warehouse", foreign_keys=[from_warehouse_id], back_populates="transfers_from")
    to_warehouse: Mapped["Warehouse"] = relationship("Warehouse", foreign_keys=[to_warehouse_id], back_populates="transfers_to")

class InventoryReservation(AuditableBase):
    """
    Reserve items for an upcoming work order.
    """
    __tablename__ = "inventory_reservations"

    item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("inventory_items.id", ondelete="CASCADE"), nullable=False, index=True)
    work_order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("work_orders.id", ondelete="CASCADE"), nullable=False)
    quantity_reserved: Mapped[int] = mapped_column(Integer, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    item: Mapped["InventoryItem"] = relationship("InventoryItem", back_populates="reservations")
    work_order: Mapped["WorkOrder"] = relationship("WorkOrder", back_populates="reservations")

class StockAlert(AuditableBase):
    """
    Configurable/Automated system stock alerts when level falls below boundary.
    """
    __tablename__ = "stock_alerts"

    item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("inventory_items.id", ondelete="CASCADE"), nullable=False, index=True)
    message: Mapped[str] = mapped_column(String(255), nullable=False)
    is_resolved: Mapped[bool] = mapped_column(default=False, nullable=False)

    item: Mapped["InventoryItem"] = relationship("InventoryItem", back_populates="stock_alerts")

class StockAudit(AuditableBase):
    """
    Log audits checking actual warehouse counts.
    """
    __tablename__ = "stock_audits"

    warehouse_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False)
    audit_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    conducted_by_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

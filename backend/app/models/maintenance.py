import uuid
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy import String, Float, Integer, ForeignKey, Date, DateTime, Text, Enum, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import AuditableBase
from app.models.enums import MaintenanceStatus, WorkOrderStatus, Priority, Severity

class MaintenancePlan(AuditableBase):
    """
    Standardized preventive plan containing triggers for assets.
    """
    __tablename__ = "maintenance_plans"

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    interval_days: Mapped[int] = mapped_column(default=30, nullable=False) # e.g. every 90 days

    schedules: Mapped[List["MaintenanceSchedule"]] = relationship("MaintenanceSchedule", back_populates="plan", cascade="all, delete-orphan")

class MaintenanceSchedule(AuditableBase):
    """
    Asset specific scheduled checks based on a plan.
    """
    __tablename__ = "maintenance_schedules"

    plan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("maintenance_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    next_due_date: Mapped[date] = mapped_column(Date, nullable=False)
    last_completed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    plan: Mapped["MaintenancePlan"] = relationship("MaintenancePlan", back_populates="schedules")
    asset: Mapped["Asset"] = relationship("Asset")

class MaintenanceRecord(AuditableBase):
    """
    Completed maintenance records.
    """
    __tablename__ = "maintenance_records"

    description: Mapped[str] = mapped_column(String(500), nullable=False)
    cost: Mapped[Optional[float]] = mapped_column(Float, default=0.0, nullable=True)
    maintenance_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    maintenance_type: Mapped[str] = mapped_column(String(50), nullable=False, default="Routine")
    vendor: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    downtime_hours: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    
    asset: Mapped["Asset"] = relationship("Asset", back_populates="maintenance_records")

class MaintenanceTask(AuditableBase):
    """
    Standardized actions within a plan or schedule.
    """
    __tablename__ = "maintenance_tasks"

    description: Mapped[str] = mapped_column(String(255), nullable=False)
    estimated_duration_minutes: Mapped[int] = mapped_column(default=60, nullable=False)

    checklists: Mapped[List["MaintenanceChecklist"]] = relationship("MaintenanceChecklist", back_populates="task", cascade="all, delete-orphan")

class MaintenanceChecklist(AuditableBase):
    """
    Individual items/checks to confirm for a task.
    """
    __tablename__ = "maintenance_checklists"

    task_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("maintenance_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    item_description: Mapped[str] = mapped_column(String(255), nullable=False)
    is_required: Mapped[bool] = mapped_column(default=True, nullable=False)

    task: Mapped["MaintenanceTask"] = relationship("MaintenanceTask", back_populates="checklists")

class WorkOrder(AuditableBase):
    """
    Core ticketing for maintenance scheduling, dispatching, execution.
    """
    __tablename__ = "work_orders"

    wo_number: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[Priority] = mapped_column(Enum(Priority), default=Priority.MEDIUM, nullable=False)
    status: Mapped[WorkOrderStatus] = mapped_column(Enum(WorkOrderStatus), default=WorkOrderStatus.OPEN, nullable=False)
    
    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)

    asset: Mapped["Asset"] = relationship("Asset", back_populates="work_orders")
    department: Mapped[Optional["Department"]] = relationship("Department", back_populates="work_orders")

    tasks: Mapped[List["WorkOrderTask"]] = relationship("WorkOrderTask", back_populates="work_order", cascade="all, delete-orphan")
    costs: Mapped[List["MaintenanceCost"]] = relationship("MaintenanceCost", back_populates="work_order", cascade="all, delete-orphan")
    history: Mapped[List["MaintenanceHistory"]] = relationship("MaintenanceHistory", back_populates="work_order", cascade="all, delete-orphan")
    assignments: Mapped[List["TechnicianAssignment"]] = relationship("TechnicianAssignment", back_populates="work_order", cascade="all, delete-orphan")
    consumptions: Mapped[List["InventoryConsumption"]] = relationship("InventoryConsumption", back_populates="work_order")
    reservations: Mapped[List["InventoryReservation"]] = relationship("InventoryReservation", back_populates="work_order", cascade="all, delete-orphan")

class WorkOrderTask(AuditableBase):
    """
    Individual steps matching an assigned Work Order.
    """
    __tablename__ = "work_order_tasks"

    work_order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("work_orders.id", ondelete="CASCADE"), nullable=False, index=True)
    task_description: Mapped[str] = mapped_column(String(255), nullable=False)
    is_completed: Mapped[bool] = mapped_column(default=False, nullable=False)

    work_order: Mapped["WorkOrder"] = relationship("WorkOrder", back_populates="tasks")

class MaintenanceCost(AuditableBase):
    """
    Financial logs linked to executing work orders.
    """
    __tablename__ = "maintenance_costs"

    work_order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("work_orders.id", ondelete="CASCADE"), nullable=False, index=True)
    cost_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. LABOR, PARTS, VENDOR
    amount: Mapped[float] = mapped_column(Float, nullable=False)

    work_order: Mapped["WorkOrder"] = relationship("WorkOrder", back_populates="costs")

class MaintenanceHistory(AuditableBase):
    """
    Static logs mapping historical work details.
    """
    __tablename__ = "maintenance_histories"

    work_order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("work_orders.id", ondelete="CASCADE"), nullable=False, index=True)
    note: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    work_order: Mapped["WorkOrder"] = relationship("WorkOrder", back_populates="history")

class FailureEvent(AuditableBase):
    """
    Assets breakdown and hardware failures details log.
    """
    __tablename__ = "failure_events"

    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    failure_description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[Severity] = mapped_column(Enum(Severity), nullable=False)
    failed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

class Downtime(AuditableBase):
    """
    Tracks asset offline durations.
    """
    __tablename__ = "downtimes"

    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

class TechnicianAssignment(AuditableBase):
    """
    Assignment of technicians to specific Work Orders.
    """
    __tablename__ = "technician_assignments"

    work_order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("work_orders.id", ondelete="CASCADE"), nullable=False, index=True)
    technician_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    work_order: Mapped["WorkOrder"] = relationship("WorkOrder", back_populates="assignments")

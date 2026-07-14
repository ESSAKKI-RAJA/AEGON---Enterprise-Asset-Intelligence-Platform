import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import AuditableBase

class DashboardMetric(AuditableBase):
    """
    General aggregated dashboard configurations and indicators data.
    """
    __tablename__ = "dashboard_metrics"

    metric_name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

class KPI(AuditableBase):
    """
    General Key Performance Indicators.
    """
    __tablename__ = "kpis"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    target_value: Mapped[float] = mapped_column(Float, nullable=False)
    current_value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)

class DepartmentKPI(AuditableBase):
    """
    Departmental level KPIs allocations.
    """
    __tablename__ = "department_kpis"

    department_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("departments.id", ondelete="CASCADE"), nullable=False, index=True)
    kpi_name: Mapped[str] = mapped_column(String(100), nullable=False)
    current_value: Mapped[float] = mapped_column(Float, nullable=False)

class FinancialKPI(AuditableBase):
    """
    Procurements / Finance specific KPIs.
    """
    __tablename__ = "financial_kpis"

    kpi_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)

class MaintenanceKPI(AuditableBase):
    """
    Maintenance workflow operations KPIs (MTTR, MTBF, etc.).
    """
    __tablename__ = "maintenance_kpis"

    kpi_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)

class InventoryKPI(AuditableBase):
    """
    Stock items inventory tracking KPIs.
    """
    __tablename__ = "inventory_kpis"

    kpi_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)

class ExecutiveSummary(AuditableBase):
    """
    Stores system health/operational textual summary templates for executive views.
    """
    __tablename__ = "executive_summaries"

    summary_text: Mapped[str] = mapped_column(Text, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

class Snapshot(AuditableBase):
    """
    Aggregations captures configurations of databases states.
    """
    __tablename__ = "snapshots"

    snapshot_name: Mapped[str] = mapped_column(String(150), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

class HistoricalMetric(AuditableBase):
    """
    General time series historical indicators log data.
    """
    __tablename__ = "historical_metrics"

    metric_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True, nullable=False)

class Trend(AuditableBase):
    """
    Analyzed directionality indicators.
    """
    __tablename__ = "trends"

    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    slope: Mapped[float] = mapped_column(Float, nullable=False)
    direction: Mapped[str] = mapped_column(String(10), nullable=False) # e.g. UP, DOWN, STABLE

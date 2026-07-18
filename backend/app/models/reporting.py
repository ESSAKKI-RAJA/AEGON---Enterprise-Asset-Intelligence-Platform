from __future__ import annotations
import uuid
from datetime import datetime
from typing import List
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import AuditableBase

class ReportTemplate(AuditableBase):
    """
    Standardized operational reports configuration layouts.
    """
    __tablename__ = "report_templates"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    layout_config: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False)

    reports: Mapped[List["Report"]] = relationship("Report", back_populates="template", cascade="all, delete-orphan")

class Report(AuditableBase):
    """
    Core instantiated report records configurations.
    """
    __tablename__ = "reports"

    title: Mapped[str] = mapped_column(String(150), nullable=False)
    template_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("report_templates.id", ondelete="RESTRICT"), nullable=False)
    parameters: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False)

    template: Mapped["ReportTemplate"] = relationship("ReportTemplate", back_populates="reports")
    executions: Mapped[List["ReportExecution"]] = relationship("ReportExecution", back_populates="report", cascade="all, delete-orphan")
    scheduled_reports: Mapped[List["ScheduledReport"]] = relationship("ScheduledReport", back_populates="report", cascade="all, delete-orphan")

class ScheduledReport(AuditableBase):
    """
    Automated triggers for reports scheduling tasks.
    """
    __tablename__ = "scheduled_reports"

    report_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True)
    cron_expression: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. '0 0 * * *'
    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    report: Mapped["Report"] = relationship("Report", back_populates="scheduled_reports")

class ReportExecution(AuditableBase):
    """
    Runtime execution records for compiled reports.
    """
    __tablename__ = "report_executions"

    report_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False) # e.g., RUNNING, COMPLETED, FAILED

    report: Mapped["Report"] = relationship("Report", back_populates="executions")
    exports: Mapped[List["ExportHistory"]] = relationship("ExportHistory", back_populates="execution", cascade="all, delete-orphan")

class ExportHistory(AuditableBase):
    """
    Export actions logs formats references.
    """
    __tablename__ = "export_histories"

    execution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("report_executions.id", ondelete="CASCADE"), nullable=False, index=True)
    format: Mapped[str] = mapped_column(String(10), nullable=False) # e.g. PDF, EXCEL, CSV
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)

    execution: Mapped["ReportExecution"] = relationship("ReportExecution", back_populates="exports")
    pdf_exports: Mapped[List["PDFExport"]] = relationship("PDFExport", back_populates="export", cascade="all, delete-orphan")
    excel_exports: Mapped[List["ExcelExport"]] = relationship("ExcelExport", back_populates="export", cascade="all, delete-orphan")
    csv_exports: Mapped[List["CSVExport"]] = relationship("CSVExport", back_populates="export", cascade="all, delete-orphan")

class PDFExport(AuditableBase):
    """
    PDF file configurations targets.
    """
    __tablename__ = "pdf_exports"

    export_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("export_histories.id", ondelete="CASCADE"), unique=True, nullable=False)
    page_count: Mapped[int] = mapped_column(nullable=False)

    export: Mapped["ExportHistory"] = relationship("ExportHistory", back_populates="pdf_exports")

class ExcelExport(AuditableBase):
    """
    Excel sheets targets layout mappings.
    """
    __tablename__ = "excel_exports"

    export_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("export_histories.id", ondelete="CASCADE"), unique=True, nullable=False)
    sheet_count: Mapped[int] = mapped_column(nullable=False)

    export: Mapped["ExportHistory"] = relationship("ExportHistory", back_populates="excel_exports")

class CSVExport(AuditableBase):
    """
    Flat CSV files targets indicators.
    """
    __tablename__ = "csv_exports"

    export_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("export_histories.id", ondelete="CASCADE"), unique=True, nullable=False)
    delimiter: Mapped[str] = mapped_column(String(5), default=",", nullable=False)

    export: Mapped["ExportHistory"] = relationship("ExportHistory", back_populates="csv_exports")

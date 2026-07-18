from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Boolean, Integer, Float, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

class TimestampMixin:
    """Provides created_at and updated_at columns."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=text('CURRENT_TIMESTAMP'), 
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=text('CURRENT_TIMESTAMP'), 
        onupdate=text('CURRENT_TIMESTAMP'), 
        nullable=False
    )

class AuditMixin:
    """Tracks who created and modified the entity."""
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    audit_id: Mapped[Optional[str]] = mapped_column(nullable=True, index=True)

class SoftDeleteMixin:
    """Allows logical deletion instead of physical deletion."""
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)

class VersionMixin:
    """Optimistic locking version tracker."""
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

class OwnershipMixin:
    """Tracks resource ownership."""
    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    owning_department_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)

class GeoLocationMixin:
    """Enables spatial/geographic coordinates tagging for physical assets."""
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    elevation: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

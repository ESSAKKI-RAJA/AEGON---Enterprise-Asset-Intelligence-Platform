from __future__ import annotations
import uuid
from typing import Optional, Any, Dict
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.models.mixins import TimestampMixin, AuditMixin, SoftDeleteMixin, VersionMixin

class AuditableBase(Base, TimestampMixin, AuditMixin, SoftDeleteMixin, VersionMixin):
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Extra metadata for flexibility
    from sqlalchemy.types import JSON
    metadata_: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSON().with_variant(JSONB, "postgresql"), nullable=True, default=dict)

    __mapper_args__ = {
        "version_id_col": VersionMixin.version
    }




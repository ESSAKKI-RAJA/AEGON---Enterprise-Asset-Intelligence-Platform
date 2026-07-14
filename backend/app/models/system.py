import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, ForeignKey, DateTime, Text, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.types import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import AuditableBase

class SystemSetting(AuditableBase):
    """
    Standard configurations mapping (key-value properties).
    """
    __tablename__ = "system_settings"

    key: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

class ApplicationConfig(AuditableBase):
    """
    Deeper environment setup (external services setup blocks).
    """
    __tablename__ = "application_configs"

    config_name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    config_data: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False)

class FeatureFlag(AuditableBase):
    """
    Enables selective software capability rollouts.
    """
    __tablename__ = "feature_flags"

    flag_name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(default=False, nullable=False)

class APIKey(AuditableBase):
    """
    Valid tokens used by third party systems to consume APIs.
    """
    __tablename__ = "api_keys"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_key: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

class Webhook(AuditableBase):
    """
    Subscribed targets to push updates.
    """
    __tablename__ = "webhooks"

    target_url: Mapped[str] = mapped_column(String(500), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. asset.created
    secret_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    logs: Mapped[List["WebhookLog"]] = relationship("WebhookLog", back_populates="webhook", cascade="all, delete-orphan")

class WebhookLog(AuditableBase):
    """
    Outbound webhook requests execution logs.
    """
    __tablename__ = "webhook_logs"

    webhook_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("webhooks.id", ondelete="CASCADE"), nullable=False, index=True)
    payload: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False)
    response_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    webhook: Mapped["Webhook"] = relationship("Webhook", back_populates="logs")

class Integration(AuditableBase):
    """
    Stores external API setup details.
    """
    __tablename__ = "integrations"

    service_name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    config: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False)
    is_connected: Mapped[bool] = mapped_column(default=False, nullable=False)

    logs: Mapped[List["IntegrationLog"]] = relationship("IntegrationLog", back_populates="integration", cascade="all, delete-orphan")

class IntegrationLog(AuditableBase):
    """
    Audits tracking incoming/outgoing integration runs.
    """
    __tablename__ = "integration_logs"

    integration_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("integrations.id", ondelete="CASCADE"), nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. SUCCESS, FAILURE
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    integration: Mapped["Integration"] = relationship("Integration", back_populates="logs")

class SystemAuditLog(AuditableBase):
    """
    Centralized system audit logs.
    """
    __tablename__ = "system_audit_logs"

    actor: Mapped[str] = mapped_column(String(255), default="system", nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    details: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False, default=dict)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

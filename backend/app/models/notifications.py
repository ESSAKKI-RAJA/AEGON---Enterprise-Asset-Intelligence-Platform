import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, ForeignKey, DateTime, Text, Boolean, Enum, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.types import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import AuditableBase
from app.models.enums import NotificationStatus, Severity

class NotificationTemplate(AuditableBase):
    """
    Standard templates for emails, push messages, SMS.
    """
    __tablename__ = "notification_templates"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    channel_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. EMAIL, PUSH, SMS
    subject_template: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    body_template: Mapped[str] = mapped_column(Text, nullable=False)

    notifications: Mapped[List["Notification"]] = relationship("Notification", back_populates="template", cascade="all, delete-orphan")

class Notification(AuditableBase):
    """
    Core notification records.
    """
    __tablename__ = "notifications"

    recipient_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    template_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("notification_templates.id", ondelete="SET NULL"), nullable=True)
    subject: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(Enum(NotificationStatus), default=NotificationStatus.UNREAD, nullable=False)

    template: Mapped[Optional["NotificationTemplate"]] = relationship("NotificationTemplate", back_populates="notifications")
    history: Mapped[List["NotificationHistory"]] = relationship("NotificationHistory", back_populates="notification", cascade="all, delete-orphan")

class NotificationChannel(AuditableBase):
    """
    Configured pathways (Twilio configuration details, SMTP details).
    """
    __tablename__ = "notification_channels"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    config: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

class NotificationHistory(AuditableBase):
    """
    Historical log of sent notifications.
    """
    __tablename__ = "notification_histories"

    notification_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("notifications.id", ondelete="CASCADE"), nullable=False, index=True)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    notification: Mapped["Notification"] = relationship("Notification", back_populates="history")

class AlertRule(AuditableBase):
    """
    Threshold definitions that trigger alerts automatically.
    """
    __tablename__ = "alert_rules"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. cpu_usage, temperature
    operator: Mapped[str] = mapped_column(String(10), nullable=False) # e.g. >, <, ==
    threshold_value: Mapped[float] = mapped_column(Float, nullable=False)

    alerts: Mapped[List["Alert"]] = relationship("Alert", back_populates="rule", cascade="all, delete-orphan")

class Alert(AuditableBase):
    """
    Asset health or system telemetry alerts.
    """
    __tablename__ = "alerts"

    rule_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("alert_rules.id", ondelete="SET NULL"), nullable=True)
    message: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[Severity] = mapped_column(Enum(Severity), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    rule: Mapped[Optional["AlertRule"]] = relationship("AlertRule", back_populates="alerts")
    history: Mapped[List["AlertHistory"]] = relationship("AlertHistory", back_populates="alert", cascade="all, delete-orphan")

class AlertHistory(AuditableBase):
    """
    Logs of alert activations and resolutions.
    """
    __tablename__ = "alert_histories"

    alert_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False, index=True)
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    alert: Mapped["Alert"] = relationship("Alert", back_populates="history")

class Reminder(AuditableBase):
    """
    Timed reminders (e.g. warranty expirations).
    """
    __tablename__ = "reminders"

    target_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    message: Mapped[str] = mapped_column(String(255), nullable=False)
    is_completed: Mapped[bool] = mapped_column(default=False, nullable=False)

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.events import EventDispatcher, DomainEvent
import logging

logger = logging.getLogger(__name__)

class NotificationEvent(DomainEvent):
    """Generic event for triggering notifications."""
    def __init__(self, channel: str, recipient: str, message: str, **kwargs):
        super().__init__(**kwargs)
        self.channel = channel
        self.recipient = recipient
        self.message = message

class AssetCriticalEvent(DomainEvent):
    """Event triggered when an asset becomes critical."""
    def __init__(self, asset_name: str, department: str, **kwargs):
        super().__init__(**kwargs)
        self.asset_name = asset_name
        self.department = department

class NotificationService:
    def __init__(self, db: Optional[AsyncSession] = None, dispatcher: Optional[EventDispatcher] = None):
        self.db = db
        self.dispatcher = dispatcher
        if self.dispatcher:
            self._register_subscriptions()

    def _register_subscriptions(self):
        """Subscribe to relevant domain events."""
        self.dispatcher.subscribe(NotificationEvent, self._handle_notification_event)
        self.dispatcher.subscribe(AssetCriticalEvent, self._handle_asset_critical_event)

    async def _handle_notification_event(self, event: NotificationEvent):
        await self.notify(event.channel, event.recipient, event.message)

    async def _handle_asset_critical_event(self, event: AssetCriticalEvent):
        await self.notify_critical_asset(event.asset_name, event.department)

    async def notify(self, channel: str, recipient: str, message: str) -> dict:
        # In a real app, this might send an email, push notification, etc.
        logger.info(f"[NOTIFY:{channel}] -> {recipient}: {message}")
        print(f"[NOTIFY:{channel}] -> {recipient}: {message}")
        return {"channel": channel, "recipient": recipient, "message": message, "status": "sent"}

    async def notify_critical_asset(self, asset_name: str, department: str) -> dict:
        return await self.notify(
            "dashboard",
            department,
            f"Asset '{asset_name}' has entered CRITICAL health status. Immediate review required."
        )

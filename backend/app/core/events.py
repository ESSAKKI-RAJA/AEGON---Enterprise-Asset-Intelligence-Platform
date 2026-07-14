from typing import Any, Callable, Dict, List, Type, Awaitable
from datetime import datetime
import uuid

class DomainEvent:
    """Base class for all domain events in the system."""
    def __init__(self, **kwargs):
        self.event_id = uuid.uuid4()
        self.timestamp = datetime.utcnow()
        for key, value in kwargs.items():
            setattr(self, key, value)

# Type alias for an async event handler
EventHandler = Callable[[DomainEvent], Awaitable[None]]

class EventDispatcher:
    """
    In-memory async event dispatcher.
    In a real distributed system, this might publish to RabbitMQ or Kafka.
    For Phase 1, it allows decoupling within the monolith.
    """
    def __init__(self):
        self._handlers: Dict[Type[DomainEvent], List[EventHandler]] = {}

    def subscribe(self, event_type: Type[DomainEvent], handler: EventHandler):
        """Subscribe an async handler to a specific domain event."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent):
        """
        Publish an event to all subscribed handlers asynchronously.
        Note: Currently awaits handlers in order. In the future, this could be
        scheduled as background tasks via asyncio.create_task or Celery.
        """
        event_type = type(event)
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    await handler(event)
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error handling event {event_type.__name__}: {str(e)}", exc_info=True)

# Global dispatcher instance for simplicity. 
# Depending on DI framework, this could be injected instead.
dispatcher = EventDispatcher()

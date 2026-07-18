from typing import Optional
from typing import Any, Callable, TypeVar, Awaitable
from functools import wraps
import time
import logging

from app.repositories.base import UnitOfWork, RepositoryException
from app.exceptions.service import translate_repo_exception
from app.core.events import EventDispatcher, dispatcher as default_dispatcher
from app.core.validation import ValidationPipeline

logger = logging.getLogger(__name__)

T = TypeVar('T')

class BaseService:
    """
    Base Enterprise Service Framework.
    Provides standard capabilities like transaction management, validation,
    event publishing, exception translation, and performance metrics.
    """
    def __init__(self, uow: UnitOfWork, event_dispatcher: Optional[EventDispatcher] = None):
        self.uow = uow
        # Default to the global dispatcher if none provided
        self.dispatcher = event_dispatcher or default_dispatcher

    async def execute_in_transaction(self, operation: Callable[[], Awaitable[T]]) -> T:
        """
        Executes a callable within the Unit of Work transaction boundary.
        Automatically commits on success, rolls back on failure, and translates exceptions.
        """
        start_time = time.time()
        try:
            async with self.uow:
                result = await operation()
            # If we reach here, __aexit__ committed successfully.
            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"Transaction completed successfully in {duration_ms:.2f}ms")
            return result
        except RepositoryException as e:
            # UoW handles rollback, we just translate
            raise translate_repo_exception(e)
        except Exception as e:
            # UoW handles rollback
            logger.error(f"Transaction failed: {str(e)}", exc_info=True)
            raise

    async def publish_event(self, event: Any) -> None:
        """Publishes a domain event asynchronously."""
        await self.dispatcher.publish(event)

    async def validate(self, pipeline: ValidationPipeline, context: Any) -> None:
        """Runs a validation pipeline and raises ValidationException on failure."""
        await pipeline.execute(context)

def track_metrics(operation_name: str):
    """
    Decorator to track service method execution time and success/failure rates.
    Logs structured metrics that can be parsed by DataDog/ELK.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            start_time = time.time()
            status = "success"
            try:
                return await func(self, *args, **kwargs)
            except Exception:
                status = "failure"
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                logger.info({
                    "metric": "service_execution",
                    "operation": operation_name,
                    "service": self.__class__.__name__,
                    "status": status,
                    "duration_ms": duration_ms
                })
        return wrapper
    return decorator

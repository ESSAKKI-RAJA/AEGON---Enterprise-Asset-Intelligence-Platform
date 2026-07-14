from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository, CacheHook, AuditHook
from app.models.reporting import Report

class ReportingRepository(BaseRepository[Report]):
    def __init__(
        self,
        session: AsyncSession,
        cache_hook: Optional[CacheHook] = None,
        audit_hook: Optional[AuditHook] = None,
    ):
        super().__init__(
            session=session,
            model_class=Report,
            cache_hook=cache_hook,
            audit_hook=audit_hook,
        )

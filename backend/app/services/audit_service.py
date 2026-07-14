from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.system import SystemAuditLog
from app.repositories.base import AuditHook, AuditLog
from typing import Optional, List, Dict, Any
import uuid

class AuditService(AuditHook):
    """
    Implements AuditHook to participate in UnitOfWork transactions.
    It takes an AsyncSession, but DOES NOT commit, leaving that to the UoW.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(self, audit: AuditLog) -> None:
        """Called automatically by repositories on CRUD operations."""
        entry = SystemAuditLog(
            actor=audit.changed_by or "system",
            action=audit.action.upper(),
            entity_type=audit.entity_type,
            entity_id=audit.entity_id,
            details={"old": audit.old_values, "new": audit.new_values}
        )
        self.db.add(entry)
        # NO COMMIT! UnitOfWork handles transaction boundaries.

    async def log_manual(self, actor: str, action: str, entity_type: str, entity_id: uuid.UUID, details: Optional[Dict[str, Any]] = None) -> SystemAuditLog:
        """For manual business event auditing."""
        entry = SystemAuditLog(
            actor=actor,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details or {},
        )
        self.db.add(entry)
        # NO COMMIT! UnitOfWork handles transaction boundaries.
        return entry

    async def history_for(self, entity_type: str, entity_id: uuid.UUID) -> List[SystemAuditLog]:
        stmt = select(SystemAuditLog).where(
            SystemAuditLog.entity_type == entity_type,
            SystemAuditLog.entity_id == entity_id
        ).order_by(SystemAuditLog.timestamp.desc())
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

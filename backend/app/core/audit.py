import json
from uuid import UUID
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import AuditHook, AuditLog as BaseAuditLog
from app.models.identity import AuditLog as DBAuditLog
import logging

logger = logging.getLogger(__name__)

def default_serializer(obj: Any) -> Any:
    """Helper to serialize UUIDs and datetimes to string."""
    if isinstance(obj, UUID):
        return str(obj)
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    return str(obj)

class DatabaseAuditHook(AuditHook):
    """
    Writes audit logs to the `audit_logs` table using the same transaction session.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def log(self, audit: BaseAuditLog):
        try:
            # Parse changed_by to UUID if possible
            user_id = None
            if audit.changed_by:
                try:
                    user_id = UUID(str(audit.changed_by))
                except ValueError:
                    pass

            db_log = DBAuditLog(
                user_id=user_id,
                action=audit.action,
                table_name=audit.entity_type,
                record_id=audit.entity_id,
                old_values=json.dumps(audit.old_values, default=default_serializer) if audit.old_values else None,
                new_values=json.dumps(audit.new_values, default=default_serializer) if audit.new_values else None,
            )
            # Add to session so it commits with the transaction
            self.session.add(db_log)
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}", exc_info=True)

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository, CacheHook, AuditHook
from app.models.procurement import PurchaseOrder

class ProcurementRepository(BaseRepository[PurchaseOrder]):
    def __init__(
        self,
        session: AsyncSession,
        cache_hook: Optional[CacheHook] = None,
        audit_hook: Optional[AuditHook] = None,
    ):
        super().__init__(
            session=session,
            model_class=PurchaseOrder,
            cache_hook=cache_hook,
            audit_hook=audit_hook,
        )

    async def get_purchase_requests(self, limit: int = 100):
        from sqlalchemy import select
        from app.models.procurement import PurchaseRequest
        stmt = select(PurchaseRequest).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_purchase_orders(self) -> int:
        from sqlalchemy import select, func
        from app.models.procurement import PurchaseOrder
        stmt = select(func.count(PurchaseOrder.id))
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_recent_purchase_orders(self, limit: int = 10):
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        from app.models.procurement import PurchaseOrder
        stmt = select(PurchaseOrder).options(selectinload(PurchaseOrder.vendor)).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

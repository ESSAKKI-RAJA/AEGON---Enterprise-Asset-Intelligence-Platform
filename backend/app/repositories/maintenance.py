from typing import Optional, List
from uuid import UUID
from datetime import date, datetime
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository, translate_db_exception, Page, QuerySpecification, FilterSpec, FilterOperator, CacheHook, AuditHook
from app.models.maintenance import MaintenanceRecord, WorkOrder
from app.models.enums import WorkOrderStatus


class MaintenanceRepository(BaseRepository[MaintenanceRecord]):
    """Maintenance domain repository specializing in completed maintenance records and work orders."""
    
    def __init__(
        self,
        session: AsyncSession,
        cache_hook: Optional[CacheHook] = None,
        audit_hook: Optional[AuditHook] = None,
    ):
        super().__init__(
            session=session,
            model_class=MaintenanceRecord,
            cache_hook=cache_hook,
            audit_hook=audit_hook,
        )

    async def find_by_asset(
        self,
        asset_id: UUID,
        page: int = 1,
        page_size: int = 20
    ) -> Page[MaintenanceRecord]:
        """Find completed maintenance records for an asset."""
        filters = [
            FilterSpec("asset_id", FilterOperator.EQ, asset_id),
            FilterSpec("is_deleted", FilterOperator.EQ, False)
        ]
        return await self.find_by_filter(filters, page, page_size)

    async def get_mtbf_summary(self, asset_id: UUID) -> dict:
        """
        Calculate MTBF (Mean Time Between Failures) in days for a specific asset
        based on the intervals between maintenance performing dates.
        """
        try:
            stmt = select(self.model_class).where(
                self.model_class.asset_id == asset_id,
                self.model_class.is_deleted == False
            ).order_by(self.model_class.date_performed.asc())
            
            result = await self.session.execute(stmt)
            records = list(result.scalars().all())
            
            if len(records) < 2:
                return {
                    "mtbf_days": None,
                    "total_events": len(records),
                    "message": "Insufficient maintenance history to calculate MTBF"
                }
            
            deltas = []
            for i in range(1, len(records)):
                delta = (records[i].date_performed - records[i-1].date_performed).days
                deltas.append(delta)
            
            avg_mtbf = sum(deltas) / len(deltas)
            return {
                "mtbf_days": avg_mtbf,
                "total_events": len(records)
            }
        except Exception as e:
            raise translate_db_exception(e)

    async def get_cost_trend(self, months: int = 6) -> list:
        from sqlalchemy import select, func
        from datetime import datetime, timedelta
        try:
            trend = []
            for i in range(months):
                start = datetime.utcnow() - timedelta(days=(months - i) * 30)
                end = start + timedelta(days=30)
                
                stmt = select(func.sum(MaintenanceRecord.cost)).where(
                    MaintenanceRecord.maintenance_date >= start,
                    MaintenanceRecord.maintenance_date < end,
                )
                res = await self.session.execute(stmt)
                cost = res.scalar() or 0
                
                trend.append({"month": start.strftime("%b %Y"), "cost": float(cost)})
            return trend
        except Exception as e:
            raise translate_db_exception(e)



class WorkOrderRepository(BaseRepository[WorkOrder]):
    """WorkOrder repository specializing in tracking execution workflows."""
    
    def __init__(
        self,
        session: AsyncSession,
        cache_hook: Optional[CacheHook] = None,
        audit_hook: Optional[AuditHook] = None,
    ):
        super().__init__(
            session=session,
            model_class=WorkOrder,
            cache_hook=cache_hook,
            audit_hook=audit_hook,
        )

    async def get_by_wo_number(self, wo_number: str) -> Optional[WorkOrder]:
        """Find a WorkOrder by its unique work order ticket number."""
        try:
            stmt = select(self.model_class).where(
                self.model_class.wo_number == wo_number,
                self.model_class.is_deleted == False
            )
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            raise translate_db_exception(e)
            
    async def find_by_status(
        self,
        status: WorkOrderStatus,
        page: int = 1,
        page_size: int = 20
    ) -> Page[WorkOrder]:
        """Find work orders matching a status."""
        filters = [
            FilterSpec("status", FilterOperator.EQ, status),
            FilterSpec("is_deleted", FilterOperator.EQ, False)
        ]
        return await self.find_by_filter(filters, page, page_size)

    async def count_all(self) -> int:
        from sqlalchemy import select, func
        try:
            stmt = select(func.count(self.model_class.id)).where(
                self.model_class.is_deleted == False
            )
            res = await self.session.execute(stmt)
            return res.scalar() or 0
        except Exception as e:
            raise translate_db_exception(e)

    async def count_by_status(self, status: WorkOrderStatus) -> int:
        from sqlalchemy import select, func
        try:
            stmt = select(func.count(self.model_class.id)).where(
                self.model_class.status == status,
                self.model_class.is_deleted == False
            )
            res = await self.session.execute(stmt)
            return res.scalar() or 0
        except Exception as e:
            raise translate_db_exception(e)

    async def find_by_spec(
        self, 
        spec: QuerySpecification
    ) -> Page[WorkOrder]:
        """Override to include eager loading of relationships."""
        from sqlalchemy.orm import selectinload
        try:
            query = select(self.model_class).options(
                selectinload(self.model_class.asset),
                selectinload(self.model_class.assignments),
                selectinload(self.model_class.costs)
            )
            
            if hasattr(self.model_class, 'is_deleted'):
                query = query.where(self.model_class.is_deleted == False)
            
            query = spec.apply_to_query(query, self.model_class)
            
            count_query = select(func.count()).select_from(self.model_class)
            if hasattr(self.model_class, 'is_deleted'):
                count_query = count_query.where(self.model_class.is_deleted == False)
            for filter_spec in spec.filters:
                count_query = count_query.where(filter_spec.to_sqlalchemy(self.model_class))
            if spec.search_query and spec.search_fields:
                search_conditions = []
                for field in spec.search_fields:
                    if hasattr(self.model_class, field):
                        search_conditions.append(getattr(self.model_class, field).ilike(f"%{spec.search_query}%"))
                if search_conditions:
                    count_query = count_query.where(or_(*search_conditions))
                    
            count_result = await self.session.execute(count_query)
            total = count_result.scalar() or 0
            
            offset = (spec.page - 1) * spec.page_size
            query = query.offset(offset).limit(spec.page_size)
            
            result = await self.session.execute(query)
            items = result.scalars().all()
            
            return Page(
                items=list(items),
                total=total,
                page=spec.page,
                page_size=spec.page_size
            )
        except Exception as e:
            raise translate_db_exception(e)

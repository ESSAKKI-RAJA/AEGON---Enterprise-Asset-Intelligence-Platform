from typing import Optional, List, Any
from uuid import UUID
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository, translate_db_exception, Page, QuerySpecification, FilterSpec, FilterOperator, CacheHook, AuditHook
from app.models.asset import Asset
from app.models.enums import AssetStatus


class AssetRepository(BaseRepository[Asset]):
    """Asset domain repository specializing in querying the actual physical assets table."""
    
    def __init__(
        self,
        session: AsyncSession,
        cache_hook: Optional[CacheHook] = None,
        audit_hook: Optional[AuditHook] = None,
    ):
        super().__init__(
            session=session,
            model_class=Asset,
            cache_hook=cache_hook,
            audit_hook=audit_hook,
        )

    async def get_by_id(self, entity_id: Any) -> Optional[Asset]:
        from sqlalchemy.orm import selectinload
        try:
            stmt = select(self.model_class).options(
                selectinload(self.model_class.category),
                selectinload(self.model_class.department)
            ).where(
                self.model_class.id == entity_id
            )
            if hasattr(self.model_class, 'is_deleted'):
                stmt = stmt.where(self.model_class.is_deleted == False)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            raise translate_db_exception(e)

    async def get_by_barcode(self, barcode: str) -> Optional[Asset]:
        """Get asset by its unique barcode tag."""
        try:
            stmt = select(self.model_class).where(
                self.model_class.barcode == barcode,
                self.model_class.is_deleted == False
            )
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            raise translate_db_exception(e)
            
    async def get_by_asset_tag(self, asset_tag: str) -> Optional[Asset]:
        """Alias for get_by_barcode to maintain compatibility."""
        return await self.get_by_barcode(asset_tag)

    async def find_by_department(
        self,
        department_id: UUID,
        page: int = 1,
        page_size: int = 20
    ) -> Page[Asset]:
        """Find assets by department."""
        filters = [
            FilterSpec("department_id", FilterOperator.EQ, department_id),
            FilterSpec("is_deleted", FilterOperator.EQ, False)
        ]
        return await self.find_by_filter(filters, page, page_size)

    async def find_by_status(
        self,
        status: AssetStatus,
        page: int = 1,
        page_size: int = 20
    ) -> Page[Asset]:
        """Find assets by status."""
        filters = [
            FilterSpec("status", FilterOperator.EQ, status),
            FilterSpec("is_deleted", FilterOperator.EQ, False)
        ]
        return await self.find_by_filter(filters, page, page_size)

    async def search_assets(
        self,
        query: str,
        page: int = 1,
        page_size: int = 20
    ) -> Page[Asset]:
        """Full-text search assets by name, barcode, serial_number, or model_number."""
        spec = QuerySpecification(
            search_query=query,
            search_fields=["name", "barcode", "serial_number", "model_number"],
            filters=[
                FilterSpec("is_deleted", FilterOperator.EQ, False)
            ],
            page=page,
            page_size=page_size
        )
        return await self.find_by_spec(spec)

    async def find_by_spec(
        self, 
        spec: QuerySpecification
    ) -> Page[Asset]:
        """Override to include eager loading of relationships."""
        from sqlalchemy.orm import selectinload
        try:
            query = select(self.model_class).options(
                selectinload(self.model_class.category),
                selectinload(self.model_class.department)
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

    async def get_summary_stats(self) -> dict:
        """Get aggregated asset statistics."""
        try:
            res_total = await self.session.execute(select(func.count(Asset.id)).where(Asset.is_deleted == False))
            res_val = await self.session.execute(select(func.sum(Asset.current_value)).where(Asset.is_deleted == False))
            res_health = await self.session.execute(select(func.avg(Asset.health_score)).where(Asset.is_deleted == False))
            res_crit = await self.session.execute(select(func.count(Asset.id)).where(Asset.health_status == "critical", Asset.is_deleted == False))
            
            return {
                "total_assets": res_total.scalar() or 0,
                "total_asset_value": float(res_val.scalar() or 0),
                "avg_health_score": round(float(res_health.scalar() or 0), 1),
                "critical_assets": res_crit.scalar() or 0,
            }
        except Exception as e:
            raise translate_db_exception(e)

    async def get_department_rankings(self) -> list:
        """Get department rankings based on asset health."""
        try:
            stmt = select(
                Asset.department_id,
                func.avg(Asset.health_score).label("avg_health"),
                func.count(Asset.id).label("asset_count"),
            ).where(Asset.is_deleted == False).group_by(Asset.department_id).order_by(func.avg(Asset.health_score).desc())
            
            result = await self.session.execute(stmt)
            rows = result.all()
            return [
                {
                    "department_id": str(r[0]) if r[0] else "Unknown", 
                    "avg_health": round(float(r[1]), 1), 
                    "asset_count": r[2]
                } 
                for r in rows
            ]
        except Exception as e:
            raise translate_db_exception(e)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel

from app.models.asset import Asset
from app.models.maintenance import WorkOrder
from app.models.enums import WorkOrderStatus

class EnterpriseKPIs(BaseModel):
    enterprise_health_score: float
    operational_efficiency: float
    maintenance_efficiency: float
    asset_availability: float

class EnterpriseKPIEngine:
    @staticmethod
    async def compute_kpis(session: AsyncSession) -> EnterpriseKPIs:
        # Asset Health
        assets_res = await session.execute(select(Asset.health_score))
        health_scores = [h for h in assets_res.scalars().all() if h is not None]
        avg_health = sum(health_scores) / len(health_scores) if health_scores else 0.0
        
        # Asset Availability: assets without open emergency work orders
        emergency_wos = await session.execute(
            select(WorkOrder.asset_id).where(
                WorkOrder.priority == "CRITICAL",
                WorkOrder.status.in_([WorkOrderStatus.OPEN, WorkOrderStatus.IN_PROGRESS])
            )
        )
        down_asset_ids = set(emergency_wos.scalars().all())
        total_assets = len(health_scores) if health_scores else 1
        availability = ((total_assets - len(down_asset_ids)) / total_assets) * 100.0
        
        # Maintenance Efficiency: % of closed work orders vs total
        all_wos_res = await session.execute(select(WorkOrder.status))
        all_wos = all_wos_res.scalars().all()
        closed_wos = [s for s in all_wos if s in [WorkOrderStatus.COMPLETED, WorkOrderStatus.CANCELLED]]
        maint_eff = (len(closed_wos) / len(all_wos) * 100.0) if all_wos else 100.0
        
        # Operational Efficiency (Blended metric)
        op_eff = (avg_health * 0.4) + (availability * 0.4) + (maint_eff * 0.2)
        
        return EnterpriseKPIs(
            enterprise_health_score=round(avg_health, 1),
            operational_efficiency=round(op_eff, 1),
            maintenance_efficiency=round(maint_eff, 1),
            asset_availability=round(availability, 1)
        )

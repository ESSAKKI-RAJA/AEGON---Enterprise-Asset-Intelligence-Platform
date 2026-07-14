from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.asset import Asset
from typing import Dict, Any

class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_executive_snapshot(self) -> Dict[str, Any]:
        stmt = select(Asset)
        result = await self.db.execute(stmt)
        assets = result.scalars().all()
        
        if not assets:
            return {"total_assets": 0, "total_value": 0, "avg_health": 0, "critical_count": 0}

        return {
            "total_assets": len(assets),
            "total_value": sum(a.current_value or 0 for a in assets),
            "avg_health": round(sum(a.health_score for a in assets) / len(assets), 1),
            "critical_count": sum(1 for a in assets if a.health_status == "critical"),
            "health_distribution": {
                status: sum(1 for a in assets if a.health_status == status)
                for status in ["excellent", "good", "fair", "poor", "critical"]
            },
        }

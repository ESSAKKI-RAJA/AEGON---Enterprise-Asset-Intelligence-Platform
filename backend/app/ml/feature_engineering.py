from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.asset import Asset
from app.ml.features.pipelines import AssetFeaturePipeline
from app.services.maintenance_service import MaintenanceService

async def extract_features(asset: Asset, db: AsyncSession) -> Dict[str, Any]:
    from app.repositories.base import UnitOfWork
    uow = UnitOfWork(db)
    maint_service = MaintenanceService(uow)
    pipeline = AssetFeaturePipeline(maint_service)
    return await pipeline.generate_features(asset)

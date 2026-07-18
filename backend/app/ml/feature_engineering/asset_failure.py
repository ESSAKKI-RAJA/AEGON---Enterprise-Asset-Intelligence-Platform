import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timezone
import uuid
import numpy as np

from app.models.asset import Asset
from app.models.maintenance import WorkOrder, MaintenanceRecord
from app.models.enums import WorkOrderStatus

import uuid
from typing import Optional

async def build_asset_failure_features(session: AsyncSession, asset_id: Optional[uuid.UUID] = None) -> pd.DataFrame:
    """
    Extracts features for Asset Failure Prediction from the database.
    Required Features: Age, Utilization, Maintenance Frequency, Repair Cost, 
    Downtime, Health Score, Environment (simulated).
    Target: Failure (Boolean - derived if health score is critically low or recent emergency WO exists).
    """
    
    # Fetch assets
    assets_stmt = select(Asset)
    if asset_id:
        assets_stmt = assets_stmt.where(Asset.id == asset_id)
    result = await session.execute(assets_stmt)
    assets = result.scalars().all()
    
    data = []
    now = datetime.now(timezone.utc)
    
    asset_ids = [asset.id for asset in assets]
    
    # Bulk fetch maintenance records
    records_by_asset = {}
    if asset_ids:
        records_stmt = select(MaintenanceRecord).where(MaintenanceRecord.asset_id.in_(asset_ids))
        records_res = await session.execute(records_stmt)
        all_records = records_res.scalars().all()
        for r in all_records:
            records_by_asset.setdefault(r.asset_id, []).append(r)
    
    for asset in assets:
        # Age in days
        if asset.purchase_date:
            if isinstance(asset.purchase_date, datetime):
                age_days = (now - asset.purchase_date.replace(tzinfo=timezone.utc)).days
            else:
                age_days = (now.date() - asset.purchase_date).days
        else:
            age_days = 0
        
        # Maintenance Frequency & Repair Cost & Downtime (simulated from records)
        records = records_by_asset.get(asset.id, [])
        
        maintenance_freq = len(records)
        total_repair_cost = sum(r.cost for r in records if r.cost)
        
        # Estimate downtime based on number of emergency/corrective maintenance records
        emergency_count = sum(1 for r in records if r.maintenance_type in ["Emergency", "Corrective"])
        downtime_hours = emergency_count * 24.0 # Estimate 24 hours downtime per emergency
        
        # Utilization (randomly simulated for now since we don't track hourly usage in DB yet)
        utilization = np.random.uniform(0.3, 0.95)
        
        # Environment factor (1 to 5, 5 being harsh)
        environment = np.random.randint(1, 6)
        
        # Target variable (Failure in next 30 days)
        # We simulate this historically: if health_score < 40 and emergency_count > 0, it likely failed.
        # This is just for training a synthetic model.
        has_failed = 1 if (asset.health_score and asset.health_score < 40) or emergency_count > 2 else 0
        
        data.append({
            "asset_id": str(asset.id),
            "age_days": age_days,
            "utilization": utilization,
            "maintenance_freq": maintenance_freq,
            "repair_cost": total_repair_cost,
            "downtime_hours": downtime_hours,
            "health_score": asset.health_score if asset.health_score else 80.0,
            "environment_factor": environment,
            "purchase_cost": float(asset.purchase_cost) if asset.purchase_cost else 5000.0,
            "category_id": hash(str(asset.category_id)) % 100,
            "has_failed": has_failed
        })
        
    df = pd.DataFrame(data)
    return df

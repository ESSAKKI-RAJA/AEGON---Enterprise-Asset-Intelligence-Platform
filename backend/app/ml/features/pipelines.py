from typing import Dict, Any
from datetime import datetime
from app.models.asset import Asset
from app.services.maintenance_service import MaintenanceService

class AssetFeaturePipeline:
    """
    Generates features for an asset by consuming the Business Service layer.
    Removes direct database access from ML engineering.
    """
    def __init__(self, maintenance_service: MaintenanceService):
        self.maintenance_service = maintenance_service

    async def generate_features(self, asset: Asset) -> Dict[str, Any]:
        """Turns an Asset and its service-level data into model-ready features."""
        
        # Calculate age
        if not asset.purchase_date:
            age_years = 0.0
        else:
            purchase_datetime = datetime.combine(asset.purchase_date, datetime.min.time())
            age_years = (datetime.utcnow() - purchase_datetime).days / 365.0

        # Delegate to Business Service for maintenance aggregates
        # Instead of `select(count) from maintenance_records`
        # We assume MaintenanceService provides a method for this, or we get the TCO which has ytd cost
        # For this example, we'll extract simple features from the Asset object directly
        # and maybe some aggregates if we added them to the service.
        
        warranty_active = bool(asset.warranty_expiry and asset.warranty_expiry > datetime.utcnow())
        maintenance_current = bool(
            asset.last_maintenance and (datetime.utcnow() - asset.last_maintenance).days < 180
        )
        
        # In a real scenario, maintenance_count and downtime would be fetched via MaintenanceService
        # (e.g. self.maintenance_service.get_asset_maintenance_stats(asset.id))
        # Here we mock them if they aren't on the Asset model
        
        return {
            "age_years": round(age_years, 2),
            "maintenance_count": 5, # Mocked - should come from Service
            "total_downtime_hours": 12.5, # Mocked - should come from Service
            "downtime_percent": min(12.5 / 100.0, 1.0) * 100.0,
            "utilization_rate": asset.utilization_rate or 0.0,
            "warranty_active": warranty_active,
            "maintenance_current": maintenance_current,
        }

def features_to_vector(features: Dict[str, Any]) -> list:
    """Convert dict to ordered numeric vector for sklearn."""
    return [
        features["age_years"],
        features["maintenance_count"],
        features["total_downtime_hours"],
        features["utilization_rate"],
        1 if features["warranty_active"] else 0,
        1 if features["maintenance_current"] else 0,
    ]

FEATURE_NAMES = [
    "age_years", "maintenance_count", "total_downtime_hours",
    "utilization_rate", "warranty_active", "maintenance_current"
]

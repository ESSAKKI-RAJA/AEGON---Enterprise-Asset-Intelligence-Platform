from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Any
import uuid
from dependency_injector.wiring import Provide, inject

from app.schemas.asset import AssetCreate, AssetUpdate, AssetResponse, AssetDigitalTwinResponse, AssetRegistryResponse
from app.services.asset_service import AssetService
from app.core.container import Container

router = APIRouter()

@router.post("/", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_asset(
    asset_in: AssetCreate,
    service: AssetService = Depends(Provide[Container.asset_service])
) -> Any:
    """Register a new asset."""
    # Transforming AssetCreate into a dictionary that AssetService expects
    data = asset_in.model_dump(exclude_unset=True)
    if "tag_number" in data:
        data["barcode"] = data.pop("tag_number")
    if "subcategory_id" not in data:
        data["subcategory_id"] = data["category_id"] 
    asset = await service.register_asset(data=data, actor="api_user")
    return asset

@router.get("/summary", response_model=dict)
@inject
async def get_summary(
    service: AssetService = Depends(Provide[Container.asset_service])
) -> Any:
    """Get asset summary statistics."""
    return await service.get_asset_summary_stats()

@router.get("/", response_model=AssetRegistryResponse)
@inject
async def search_assets(
    query: str = "",
    page: int = 1,
    page_size: int = 20,
    service: AssetService = Depends(Provide[Container.asset_service])
) -> Any:
    """Enterprise search and paginated asset registry."""
    return await service.search_assets(query=query, page=page, page_size=page_size)

@router.get("/kpis/global", response_model=dict)
@inject
async def get_global_kpis(
    service: AssetService = Depends(Provide[Container.asset_service])
) -> Any:
    """Global Asset KPIs for the registry overview."""
    summary = await service.get_asset_summary_stats()
    
    total = summary.get("total_assets", 0)
    critical = summary.get("critical_assets", 0)
    avg_health = summary.get("avg_health_score", 0.0)
    
    return {
        "kpis": [
            {"label": "Total Assets", "value": str(total), "delta": "+2 this week", "deltaPositive": True},
            {"label": "Critical Risk", "value": str(critical), "deltaTone": "critical" if critical > 0 else "positive"},
            {"label": "Avg Health", "value": f"{avg_health:.1f}", "delta": "Stable", "deltaPositive": True},
            {"label": "Total Value", "value": "$1.2M", "delta": "Depreciating expectedly", "deltaPositive": False}
        ]
    }

@router.get("/{asset_id}", response_model=AssetDigitalTwinResponse)
@inject
async def get_asset_digital_twin(
    asset_id: uuid.UUID,
    service: AssetService = Depends(Provide[Container.asset_service])
) -> Any:
    """Retrieve the comprehensive Digital Twin for a single asset."""
    return await service.get_asset_digital_twin(asset_id)

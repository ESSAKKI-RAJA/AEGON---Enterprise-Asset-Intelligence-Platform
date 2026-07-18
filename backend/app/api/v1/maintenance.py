from fastapi import APIRouter, Depends
from typing import Any
from dependency_injector.wiring import Provide, inject

from app.services.maintenance_service import MaintenanceService
from app.core.container import Container

from app.schemas.maintenance import MaintenanceOverviewResponse

router = APIRouter()

@router.get("/", response_model=MaintenanceOverviewResponse)
@inject
async def get_maintenance(
    service: MaintenanceService = Depends(Provide[Container.maintenance_service])
) -> Any:
    """Enterprise Maintenance Overview and KPIs."""
    return await service.get_maintenance_overview()

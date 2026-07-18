from fastapi import APIRouter, Depends
from typing import Any
from dependency_injector.wiring import Provide, inject

from app.services.procurement_service import ProcurementService
from app.core.container import Container

from app.schemas.procurement import ProcurementOverviewResponse

router = APIRouter()

@router.get("/", response_model=ProcurementOverviewResponse)
@inject
async def get_procurement(
    service: ProcurementService = Depends(Provide[Container.procurement_service])
) -> Any:
    """Enterprise Procurement Overview and KPIs."""
    return await service.get_procurement_overview()

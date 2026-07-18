from fastapi import APIRouter, Depends
from typing import Any
from dependency_injector.wiring import Provide, inject

from app.services.inventory_service import InventoryService
from app.core.container import Container

from app.schemas.inventory import InventoryOverviewResponse

router = APIRouter()

@router.get("/", response_model=InventoryOverviewResponse)
@inject
async def get_inventory(
    service: InventoryService = Depends(Provide[Container.inventory_service])
) -> Any:
    """Enterprise Inventory Overview and KPIs."""
    return await service.get_inventory_overview()

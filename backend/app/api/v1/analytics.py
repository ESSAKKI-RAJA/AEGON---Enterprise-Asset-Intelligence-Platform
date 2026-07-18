from fastapi import APIRouter, Depends
from typing import Any
from dependency_injector.wiring import Provide, inject

from app.services.analytics_service import AnalyticsService
from app.core.container import Container

from app.schemas.analytics import AnalyticsOverviewResponse
from app.schemas.response import StandardResponse

router = APIRouter()

@router.get("/dashboards/executive", response_model=StandardResponse[dict])
@inject
async def get_executive_dashboard(
    service: AnalyticsService = Depends(Provide[Container.analytics_service])
) -> Any:
    payload = await service.full_dashboard_payload()
    return StandardResponse(data=payload)

@router.get("/", response_model=AnalyticsOverviewResponse)
@inject
async def get_enterprise_analytics(
    service: AnalyticsService = Depends(Provide[Container.analytics_service])
) -> Any:
    """Enterprise Cross-Functional Analytics."""
    return await service.get_enterprise_analytics()

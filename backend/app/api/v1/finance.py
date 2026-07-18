from fastapi import APIRouter, Depends
from typing import List, Any
from dependency_injector.wiring import Provide, inject

from app.services.finance_service import FinanceService
from app.core.container import Container

from app.schemas.finance import FinanceOverviewResponse

router = APIRouter()

@router.get("/", response_model=FinanceOverviewResponse)
@inject
async def get_finance(
    service: FinanceService = Depends(Provide[Container.finance_service])
) -> Any:
    """Enterprise Finance Overview and KPIs."""
    return await service.get_finance_overview()

@router.get("/budgets", response_model=List[dict])
@inject
async def get_budgets(
    service: FinanceService = Depends(Provide[Container.finance_service])
) -> Any:
    return await service.get_budgets()

@router.get("/roi", response_model=dict)
@inject
async def get_roi_analysis(
    service: FinanceService = Depends(Provide[Container.finance_service])
) -> Any:
    return await service.get_roi_analysis()

@router.get("/expenses", response_model=List[dict])
@inject
async def get_expenses(
    service: FinanceService = Depends(Provide[Container.finance_service])
) -> Any:
    return await service.get_expenses()

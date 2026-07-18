from fastapi import APIRouter, Depends, Query
from typing import Any
from app.api.deps import get_uow, get_current_user
from app.services.search_service import SearchService
from app.repositories.base import UnitOfWork
from app.core.events import dispatcher

router = APIRouter()

def get_search_service(uow: UnitOfWork = Depends(get_uow)) -> SearchService:
    return SearchService(uow=uow, event_dispatcher=dispatcher)

@router.get("/", response_model=dict, dependencies=[Depends(get_current_user)])
async def global_search(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, description="Max results"),
    search_service: SearchService = Depends(get_search_service)
) -> Any:
    results = await search_service.search(query=q, limit=limit)
    return {"data": results}

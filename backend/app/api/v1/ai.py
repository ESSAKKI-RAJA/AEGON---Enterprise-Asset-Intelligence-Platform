from fastapi import APIRouter, Depends, status
from typing import List, Any
from dependency_injector.wiring import Provide, inject

from app.services.ai_service import AIService
from app.services.copilot_service import CopilotService
from app.services.search_service import SearchService
from app.core.container import Container
from app.api.deps import get_current_user
from app.models.identity import User
import uuid

router = APIRouter()

@router.post("/copilot/ask", response_model=dict)
@inject
async def ask_copilot(
    body: dict,
    current_user: User = Depends(get_current_user),
    service: CopilotService = Depends(Provide[Container.copilot_service])
) -> Any:
    conversation_id = body.get("conversation_id")
    if not conversation_id:
        conversation_id = uuid.uuid4()
    else:
        conversation_id = uuid.UUID(conversation_id)

    res = await service.ask(
        conversation_id=conversation_id,
        user_query=body.get("query"),
        user_id=current_user.id
    )
    return {
        "data": {
            "conversation_id": str(conversation_id),
            "response": res
        }
    }

@router.get("/search", response_model=dict)
@inject
async def global_search(
    q: str,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    service: SearchService = Depends(Provide[Container.search_service])
) -> Any:
    results = await service.search(query=q, limit=limit)
    return {
        "data": results
    }
